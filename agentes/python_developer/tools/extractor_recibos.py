#!/usr/bin/env python3
"""
Module: extractor_recibos.py
Purpose: OCR-based receipt extractor — images to Keystone 20-column schema dict
Dependencies: see requirements.txt
Usage: python extractor_recibos.py <image_path> [--save]
Install: pip install -r agentes/python_developer/tools/requirements.txt
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional Tesseract binary override via env var
# Set TESSERACT_CMD to the full path if tesseract is not on PATH
# e.g.  TESSERACT_CMD="C:/Program Files/Tesseract-OCR/tesseract.exe"
# ---------------------------------------------------------------------------
import os

_TESSERACT_CMD = os.getenv("TESSERACT_CMD")


# ---------------------------------------------------------------------------
# Lazy imports so missing libs give a clean error message
# ---------------------------------------------------------------------------
def _import_pillow():
    """Import Pillow modules, raising ImportError with install hint on failure."""
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
        return Image, ImageEnhance, ImageFilter, ImageOps
    except ImportError as exc:
        logger.error("Pillow not installed. Run: pip install Pillow==10.3.0")
        raise ImportError("Pillow required") from exc


def _import_pytesseract():
    """Import pytesseract, setting custom cmd if env var is provided."""
    try:
        import pytesseract
        if _TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD
            logger.info("Tesseract binary set to: %s", _TESSERACT_CMD)
        return pytesseract
    except ImportError as exc:
        logger.error("pytesseract not installed. Run: pip install pytesseract==0.3.13")
        raise ImportError("pytesseract required") from exc


# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------

def preprocess_image(image_path: Path):
    """Convert image to grayscale, binarize and enhance contrast for OCR."""
    Image, ImageEnhance, ImageFilter, ImageOps = _import_pillow()

    try:
        img = Image.open(image_path)
    except (FileNotFoundError, OSError) as exc:
        logger.error("Cannot open image '%s': %s", image_path, exc)
        raise

    logger.info("Original mode: %s, size: %s", img.mode, img.size)

    # 1. Convert to grayscale
    img = img.convert("L")

    # 2. Increase contrast before binarization
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # 3. Sharpness — helps with blurry receipts
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)

    # 4. Binarize with Otsu-like auto-threshold via point()
    #    threshold = 140 is a reasonable midpoint for receipt paper
    threshold: int = int(os.getenv("OCR_THRESHOLD", "140"))
    img = img.point(lambda px: 255 if px > threshold else 0, "1")

    # 5. Convert back to "L" for pytesseract compatibility
    img = img.convert("L")

    logger.info("Preprocessing done. Output mode: %s, size: %s", img.mode, img.size)
    return img


# ---------------------------------------------------------------------------
# OCR
# ---------------------------------------------------------------------------

def extract_text(image_path: Path) -> str:
    """Run pytesseract on the preprocessed image and return raw OCR text."""
    pytesseract = _import_pytesseract()

    processed = preprocess_image(image_path)

    try:
        # lang="spa+eng" handles Spanish receipts with English numbers
        text: str = pytesseract.image_to_string(
            processed,
            lang=os.getenv("TESSERACT_LANG", "spa+eng"),
            config="--psm 6",       # Assume uniform block of text
        )
    except Exception as exc:
        logger.error("pytesseract OCR failed: %s", exc)
        raise

    logger.info("OCR extracted %d characters", len(text))
    logger.debug("Raw OCR text:\n%s", text)
    return text


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

# --- Date ---

_DATE_PATTERNS: list[tuple[str, str]] = [
    # DD/MM/YYYY or DD-MM-YYYY
    (r"\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})\b", "dmy"),
    # YYYY/MM/DD or YYYY-MM-DD
    (r"\b(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})\b", "ymd"),
    # DD de MES de YYYY (Spanish)
    (
        r"\b(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
        r"\s+(?:de\s+)?(\d{4})\b",
        "dmonthname_y",
    ),
]

_MONTH_NAMES: dict[str, str] = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}


def parse_fecha(text: str) -> Optional[str]:
    """Extract and normalize the first date found in OCR text to YYYY-MM-DD."""
    lower = text.lower()
    for pattern, fmt in _DATE_PATTERNS:
        m = re.search(pattern, lower)
        if not m:
            continue
        try:
            if fmt == "dmy":
                d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
                return f"{y}-{mo}-{d}"
            if fmt == "ymd":
                y, mo, d = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
                return f"{y}-{mo}-{d}"
            if fmt == "dmonthname_y":
                d = m.group(1).zfill(2)
                mo = _MONTH_NAMES.get(m.group(2), "01")
                y = m.group(3)
                return f"{y}-{mo}-{d}"
        except (IndexError, ValueError) as exc:
            logger.warning("Date normalization failed for match '%s': %s", m.group(0), exc)
            continue
    logger.debug("No date found in text")
    return None


# --- Proveedor ---

def parse_proveedor(text: str) -> Optional[str]:
    """Extract company/store name from the first non-empty lines of the receipt."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    # The store name is typically one of the first 3 non-trivial lines
    # Skip lines that are purely numeric or very short (≤2 chars)
    for line in lines[:5]:
        if len(line) > 3 and not re.match(r"^\d+$", line):
            return line
    return lines[0] if lines else None


# --- NIT ---

_NIT_PATTERN = re.compile(
    r"(?:NIT|Nit|nit)[:\s]*"
    r"(\d[\d\.\s]{5,14}[\-–]?\d?)",
    re.IGNORECASE,
)


def parse_nit(text: str) -> Optional[str]:
    """Extract Colombian NIT (tax ID) from OCR text."""
    m = _NIT_PATTERN.search(text)
    if m:
        raw = m.group(1).strip()
        logger.debug("NIT raw match: '%s'", raw)
        return raw
    return None


# --- Currency amounts ---

def _parse_currency_value(text: str, labels: list[str]) -> Optional[float]:
    """Find the first currency amount preceded by any of the given label keywords."""
    for label in labels:
        pattern = re.compile(
            rf"{re.escape(label)}"
            r"[:\s\$]*"
            r"([\d\.,]+)",
            re.IGNORECASE,
        )
        m = pattern.search(text)
        if m:
            raw = m.group(1).replace(".", "").replace(",", ".")
            try:
                value = float(raw)
                logger.debug("Amount match for '%s': %s → %s", label, m.group(1), value)
                return value
            except ValueError:
                logger.warning("Could not parse amount '%s' for label '%s'", raw, label)
    return None


def parse_subtotal(text: str) -> Optional[float]:
    """Extract subtotal amount from OCR text."""
    return _parse_currency_value(
        text,
        ["SUBTOTAL", "Sub total", "Sub-total", "NETO", "BASE"],
    )


def parse_iva(text: str) -> Optional[float]:
    """Extract IVA (tax) amount from OCR text."""
    return _parse_currency_value(
        text,
        ["IVA", "I.V.A", "TAX", "IMPUESTO"],
    )


def parse_total(text: str) -> Optional[float]:
    """Extract total amount due from OCR text."""
    return _parse_currency_value(
        text,
        ["TOTAL A PAGAR", "VALOR TOTAL", "GRAN TOTAL", "TOTAL", "A PAGAR", "IMPORTE TOTAL"],
    )


# --- Divisa ---

def parse_divisa(text: str) -> str:
    """Detect currency; defaults to COP unless USD/EUR explicitly found."""
    upper = text.upper()
    if "USD" in upper or "U$S" in upper or "DOLLAR" in upper:
        return "USD"
    if "EUR" in upper or "EURO" in upper:
        return "EUR"
    return "COP"


# --- Método de pago ---

_METODO_KEYWORDS: dict[str, list[str]] = {
    "EFECTIVO": ["EFECTIVO", "CASH", "EN EFECTIVO"],
    "TARJETA": ["TARJETA", "CREDITO", "DÉBITO", "DEBITO", "VISA", "MASTERCARD", "AMEX"],
    "NEQUI": ["NEQUI"],
    "DAVIPLATA": ["DAVIPLATA"],
    "TRANSFERENCIA": ["TRANSFERENCIA", "PSE", "ACH"],
    "DATAFONO": ["DATAFONO", "DATÁFONO"],
}


def parse_metodo_pago(text: str) -> Optional[str]:
    """Detect payment method keyword in OCR text."""
    upper = text.upper()
    for metodo, keywords in _METODO_KEYWORDS.items():
        if any(kw in upper for kw in keywords):
            logger.debug("Payment method detected: %s", metodo)
            return metodo
    return None


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

def extract_receipt(image_path: Path) -> dict:
    """Run full OCR + parsing pipeline on a receipt image and return structured dict."""
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    suffix = image_path.suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        raise ValueError(f"Unsupported image format '{suffix}'. Use JPG or PNG.")

    raw_text = extract_text(image_path)

    result: dict = {
        "fecha": parse_fecha(raw_text),
        "proveedor": parse_proveedor(raw_text),
        "nit": parse_nit(raw_text),
        "subtotal": parse_subtotal(raw_text),
        "iva": parse_iva(raw_text),
        "total": parse_total(raw_text),
        "divisa": parse_divisa(raw_text),
        "metodo_pago": parse_metodo_pago(raw_text),
        "texto_crudo": raw_text,
        "archivo_fuente": image_path.name,
    }

    logger.info(
        "Extraction complete — fecha=%s, proveedor=%s, total=%s",
        result["fecha"],
        result["proveedor"],
        result["total"],
    )
    return result


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_result(result: dict, image_path: Path) -> Path:
    """Write the result dict as a JSON file alongside the source image."""
    output_path = image_path.with_suffix(".json")
    try:
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        logger.info("Result saved to: %s", output_path)
    except OSError as exc:
        logger.error("Could not write output JSON '%s': %s", output_path, exc)
        raise
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract structured data from a receipt image (JPG/PNG) via OCR.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python extractor_recibos.py recibo.jpg\n"
            "  python extractor_recibos.py recibo.png --save\n"
            "  python extractor_recibos.py recibo.jpg --log-level DEBUG\n"
        ),
    )
    parser.add_argument("image", help="Path to the receipt image (JPG or PNG)")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save extracted data as a .json file alongside the image",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return parser


def run(args: argparse.Namespace) -> None:
    """Core execution: validate input, extract, print, optionally save."""
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    image_path = Path(args.image).resolve()
    logger.info("Processing receipt: %s", image_path)

    result = extract_receipt(image_path)

    # Output to stdout — pretty-printed JSON (texto_crudo can be verbose)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.save:
        saved_path = save_result(result, image_path)
        logger.info("Saved: %s", saved_path)


def main() -> None:
    """Entry point with top-level try/except per Keystone Script Standard."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        run(args)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        sys.exit(2)
    except Exception as exc:
        logger.error("Unhandled error: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
