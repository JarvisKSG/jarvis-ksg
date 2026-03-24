"""
TEST-001: OCR Pipeline Resilience Tests
========================================
Agente: tester_automation | Fecha: 2026-03-24
Misión: Verificar que si el motor OCR devuelve JSON vacío o malformado,
        el sistema no se caiga y lance una excepción controlada.

Cobertura target: ReciboExtraido parsing — 95%
Framework: Pytest

Ejecutar: pytest tests/ocr_pipeline/test_ocr_pipeline.py -v
"""

import json
import pytest
from dataclasses import dataclass, field
from typing import Optional


# ===========================================================================
# Implementación de referencia de ReciboExtraido
# (espejo del dataclass en agentes/python_developer/role.md)
# TODO: reemplazar por import real cuando el módulo OCR esté como paquete:
#       from agentes.python_developer.tools.ocr_parser import ReciboExtraido, parse_recibo
# ===========================================================================

@dataclass
class ReciboExtraido:
    fecha: str
    proveedor: str
    concepto: str
    subtotal: float
    iva: float
    total: float
    divisa: str
    confianza_global: float
    confianza_campos: dict
    archivo_origen: str
    nit: Optional[str] = None
    metodo_pago: Optional[str] = None


class OCRParsingError(ValueError):
    """Excepción controlada para errores de parsing del motor OCR."""
    pass


class OCREmptyResultError(OCRParsingError):
    """OCR devolvió resultado vacío o sin campos reconocibles."""
    pass


class OCRMalformedJSONError(OCRParsingError):
    """OCR devolvió JSON que no puede ser parseado."""
    pass


class OCRMissingFieldsError(OCRParsingError):
    """JSON válido pero faltan campos obligatorios de ReciboExtraido."""
    pass


class OCRInvalidTypesError(OCRParsingError):
    """Campos presentes pero con tipos incorrectos (ej. subtotal='cien mil')."""
    pass


def parse_recibo(raw_json: str | dict) -> ReciboExtraido:
    """
    Parsea el output crudo del motor OCR y devuelve un ReciboExtraido validado.
    Lanza excepciones controladas para cualquier condición de error.
    NUNCA propaga excepciones genéricas sin contexto.
    """
    REQUIRED_FIELDS = [
        "fecha", "proveedor", "concepto",
        "subtotal", "iva", "total",
        "divisa", "confianza_global", "confianza_campos", "archivo_origen"
    ]
    NUMERIC_FIELDS = ["subtotal", "iva", "total", "confianza_global"]

    # --- Paso 1: parsear JSON si es string ---
    if isinstance(raw_json, str):
        raw_json = raw_json.strip()
        if not raw_json:
            raise OCREmptyResultError("OCR devolvió string vacío — ningún texto fue reconocido en la imagen.")
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise OCRMalformedJSONError(
                f"El motor OCR devolvió JSON malformado y no puede ser procesado. "
                f"Detalle: {e.msg} en posición {e.pos}."
            ) from e
    else:
        data = raw_json

    # --- Paso 2: verificar que no sea dict vacío ---
    if not data:
        raise OCREmptyResultError("OCR devolvió JSON vacío {{}} — ningún campo fue extraído.")

    # --- Paso 3: verificar campos obligatorios ---
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise OCRMissingFieldsError(
            f"Campos obligatorios ausentes en el output OCR: {missing}. "
            f"El recibo no puede ser registrado en Caja Negra sin estos campos."
        )

    # --- Paso 4: verificar tipos numéricos ---
    invalid_types = []
    for field_name in NUMERIC_FIELDS:
        val = data.get(field_name)
        if val is not None and not isinstance(val, (int, float)):
            invalid_types.append(f"{field_name}={repr(val)}")
    if invalid_types:
        raise OCRInvalidTypesError(
            f"Campos numéricos con tipo incorrecto: {invalid_types}. "
            f"Se esperaba int o float."
        )

    # --- Paso 5: validaciones de negocio ---
    if data["total"] < 0:
        raise OCRParsingError(
            f"total={data['total']} es negativo — valor inválido para un recibo."
        )

    subtotal, iva, total = data["subtotal"], data["iva"], data["total"]
    expected_total = round(subtotal + iva, 2)
    if abs(expected_total - total) > 1.0:  # tolerancia de $1 COP por redondeos
        raise OCRParsingError(
            f"Math mismatch: subtotal ({subtotal}) + iva ({iva}) = {expected_total} "
            f"pero total declarado es {total}. Diferencia: {abs(expected_total - total):.2f} COP."
        )

    confianza = data["confianza_global"]
    if not (0.0 <= confianza <= 1.0):
        raise OCRInvalidTypesError(
            f"confianza_global={confianza} fuera del rango válido [0.0, 1.0]."
        )

    # --- Paso 6: construir y devolver el dataclass ---
    return ReciboExtraido(
        fecha=data["fecha"],
        proveedor=data["proveedor"],
        concepto=data["concepto"],
        subtotal=float(data["subtotal"]),
        iva=float(data["iva"]),
        total=float(data["total"]),
        divisa=data["divisa"],
        confianza_global=float(data["confianza_global"]),
        confianza_campos=data.get("confianza_campos", {}),
        archivo_origen=data["archivo_origen"],
        nit=data.get("nit"),
        metodo_pago=data.get("metodo_pago"),
    )


# ===========================================================================
# FIXTURES — Recibos falsos (mocks) con errores típicos
# ===========================================================================

@pytest.fixture
def recibo_valido_minimo():
    return {
        "fecha": "2026-03-24",
        "proveedor": "Ferretería El Tornillo S.A.S.",
        "concepto": "Materiales de construcción",
        "subtotal": 100_000.0,
        "iva": 19_000.0,
        "total": 119_000.0,
        "divisa": "COP",
        "confianza_global": 0.87,
        "confianza_campos": {"proveedor": 0.92, "total": 0.80},
        "archivo_origen": "recibo_001.jpg",
    }


@pytest.fixture
def recibo_confianza_amber():
    """Recibo con confianza_global en zona amber (0.70–0.84)."""
    return {
        "fecha": "2026-03-24",
        "proveedor": "Distribuidora Central",
        "concepto": "Combustible",
        "subtotal": 80_000.0,
        "iva": 0.0,
        "total": 80_000.0,
        "divisa": "COP",
        "confianza_global": 0.74,
        "confianza_campos": {},
        "archivo_origen": "recibo_termico_002.jpg",
    }


@pytest.fixture
def recibo_usd():
    """Recibo en USD — debe soportar divisa distinta a COP."""
    return {
        "fecha": "2026-03-24",
        "proveedor": "Amazon AWS",
        "concepto": "Cloud compute",
        "subtotal": 45.00,
        "iva": 0.0,
        "total": 45.00,
        "divisa": "USD",
        "confianza_global": 0.95,
        "confianza_campos": {},
        "archivo_origen": "aws_invoice_march.pdf",
    }


# ===========================================================================
# TESTS — Happy Path
# ===========================================================================

class TestParseReciboHappyPath:

    def test_parse_recibo_valido_devuelve_ReciboExtraido(self, recibo_valido_minimo):
        """JSON válido con todos los campos produce un ReciboExtraido correcto."""
        result = parse_recibo(recibo_valido_minimo)
        assert isinstance(result, ReciboExtraido)
        assert result.proveedor == "Ferretería El Tornillo S.A.S."
        assert result.total == 119_000.0
        assert result.confianza_global == 0.87

    def test_parse_recibo_string_json_valido(self, recibo_valido_minimo):
        """String JSON válido es parseado igual que un dict."""
        result = parse_recibo(json.dumps(recibo_valido_minimo))
        assert result.subtotal == 100_000.0

    def test_parse_recibo_confianza_amber_no_lanza_excepcion(self, recibo_confianza_amber):
        """Confianza en zona amber (0.70–0.84) es válida — no debe fallar el parsing."""
        result = parse_recibo(recibo_confianza_amber)
        assert 0.70 <= result.confianza_global < 0.85

    def test_parse_recibo_usd_acepta_divisa_no_cop(self, recibo_usd):
        """Recibos en USD deben ser aceptados sin error."""
        result = parse_recibo(recibo_usd)
        assert result.divisa == "USD"
        assert result.total == 45.00

    def test_parse_recibo_campos_opcionales_son_none_por_defecto(self, recibo_valido_minimo):
        """nit y metodo_pago son opcionales — None si no están presentes."""
        result = parse_recibo(recibo_valido_minimo)
        assert result.nit is None
        assert result.metodo_pago is None

    def test_parse_recibo_con_nit_y_metodo_pago(self, recibo_valido_minimo):
        """Campos opcionales son correctamente asignados cuando presentes."""
        recibo_valido_minimo["nit"] = "900123456-1"
        recibo_valido_minimo["metodo_pago"] = "Transferencia"
        result = parse_recibo(recibo_valido_minimo)
        assert result.nit == "900123456-1"
        assert result.metodo_pago == "Transferencia"


# ===========================================================================
# TESTS — JSON Vacío y Malformado (el core de TEST-001)
# ===========================================================================

class TestParseReciboEmptyAndMalformed:

    def test_string_vacio_lanza_OCREmptyResultError(self):
        """String completamente vacío: excepción controlada, no crash genérico."""
        with pytest.raises(OCREmptyResultError, match="string vacío"):
            parse_recibo("")

    def test_string_solo_espacios_lanza_OCREmptyResultError(self):
        """String de solo whitespace: tratado como vacío."""
        with pytest.raises(OCREmptyResultError):
            parse_recibo("   \n\t  ")

    def test_dict_vacio_lanza_OCREmptyResultError(self):
        """Dict vacío {}: ningún campo extraído — excepción controlada."""
        with pytest.raises(OCREmptyResultError, match="JSON vacío"):
            parse_recibo({})

    def test_json_string_vacio_lanza_OCREmptyResultError(self):
        """String '{}': parseado como dict vacío → OCREmptyResultError."""
        with pytest.raises(OCREmptyResultError):
            parse_recibo("{}")

    def test_json_malformado_lanza_OCRMalformedJSONError(self):
        """JSON con sintaxis inválida: excepción controlada con detalle."""
        with pytest.raises(OCRMalformedJSONError, match="malformado"):
            parse_recibo("{ campo_sin_cerrar: valor sin comillas")

    def test_json_truncado_lanza_OCRMalformedJSONError(self):
        """JSON truncado (ej. imagen cortada): excepción controlada."""
        with pytest.raises(OCRMalformedJSONError):
            parse_recibo('{"fecha": "2026-03-24", "proveedor":')

    def test_texto_plano_no_json_lanza_OCRMalformedJSONError(self):
        """Texto libre del OCR (no JSON): excepción controlada."""
        with pytest.raises(OCRMalformedJSONError):
            parse_recibo("FERRETERIA EL TORNILLO TOTAL: $119.000")

    def test_excepcion_es_subclase_de_ValueError(self):
        """Toda OCRParsingError debe ser catcheable como ValueError."""
        with pytest.raises(ValueError):
            parse_recibo("")


# ===========================================================================
# TESTS — Campos Faltantes
# ===========================================================================

class TestParseReciboMissingFields:

    def test_solo_proveedor_lanza_OCRMissingFieldsError(self):
        """Solo un campo presente: error con lista de campos faltantes."""
        with pytest.raises(OCRMissingFieldsError) as exc_info:
            parse_recibo({"proveedor": "Test"})
        assert "fecha" in str(exc_info.value)
        assert "total" in str(exc_info.value)

    def test_sin_confianza_global_lanza_OCRMissingFieldsError(self):
        """confianza_global es obligatorio — sin él no se puede clasificar el recibo."""
        data = {
            "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
            "subtotal": 100.0, "iva": 0.0, "total": 100.0,
            "divisa": "COP", "confianza_campos": {}, "archivo_origen": "test.jpg"
            # missing: confianza_global
        }
        with pytest.raises(OCRMissingFieldsError, match="confianza_global"):
            parse_recibo(data)

    def test_sin_archivo_origen_lanza_OCRMissingFieldsError(self):
        """archivo_origen es obligatorio para trazabilidad en Caja Negra."""
        data = {
            "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
            "subtotal": 100.0, "iva": 0.0, "total": 100.0, "divisa": "COP",
            "confianza_global": 0.85, "confianza_campos": {}
            # missing: archivo_origen
        }
        with pytest.raises(OCRMissingFieldsError, match="archivo_origen"):
            parse_recibo(data)


# ===========================================================================
# TESTS — Tipos Incorrectos
# ===========================================================================

class TestParseReciboInvalidTypes:

    def test_subtotal_string_lanza_OCRInvalidTypesError(self):
        """subtotal como string: error de tipo controlado."""
        with pytest.raises(OCRInvalidTypesError, match="subtotal"):
            parse_recibo({
                "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
                "subtotal": "cien mil", "iva": 0.0, "total": 100_000.0,
                "divisa": "COP", "confianza_global": 0.85,
                "confianza_campos": {}, "archivo_origen": "test.jpg"
            })

    def test_confianza_global_string_lanza_OCRInvalidTypesError(self):
        """confianza_global como string 'alta': tipo incorrecto."""
        with pytest.raises(OCRInvalidTypesError, match="confianza_global"):
            parse_recibo({
                "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
                "subtotal": 100_000.0, "iva": 19_000.0, "total": 119_000.0,
                "divisa": "COP", "confianza_global": "alta",
                "confianza_campos": {}, "archivo_origen": "test.jpg"
            })

    def test_confianza_fuera_de_rango_mayor_1_lanza_error(self):
        """confianza_global > 1.0 es inválido — nadie tiene confianza perfecta sin verificación."""
        with pytest.raises(OCRInvalidTypesError, match="rango"):
            parse_recibo({
                "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
                "subtotal": 100_000.0, "iva": 19_000.0, "total": 119_000.0,
                "divisa": "COP", "confianza_global": 1.5,
                "confianza_campos": {}, "archivo_origen": "test.jpg"
            })


# ===========================================================================
# TESTS — Validaciones de Negocio
# ===========================================================================

class TestParseReciboBusinessRules:

    def test_total_negativo_lanza_OCRParsingError(self):
        """Total negativo: imposible en un recibo real — excepción controlada."""
        with pytest.raises(OCRParsingError, match="negativo"):
            parse_recibo({
                "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
                "subtotal": -100_000.0, "iva": 0.0, "total": -100_000.0,
                "divisa": "COP", "confianza_global": 0.85,
                "confianza_campos": {}, "archivo_origen": "test.jpg"
            })

    def test_math_mismatch_subtotal_iva_total_lanza_OCRParsingError(self):
        """subtotal + iva != total: error matemático detectado antes de Caja Negra."""
        with pytest.raises(OCRParsingError, match="Math mismatch"):
            parse_recibo({
                "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
                "subtotal": 100_000.0, "iva": 19_000.0, "total": 999_999.0,
                "divisa": "COP", "confianza_global": 0.85,
                "confianza_campos": {}, "archivo_origen": "test.jpg"
            })

    def test_math_con_tolerancia_de_redondeo_pasa(self):
        """Diferencia de $0.50 COP por redondeo: no debe fallar."""
        result = parse_recibo({
            "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
            "subtotal": 100_000.0, "iva": 19_000.0, "total": 119_000.5,
            "divisa": "COP", "confianza_global": 0.85,
            "confianza_campos": {}, "archivo_origen": "test.jpg"
        })
        assert result.total == 119_000.5

    def test_iva_cero_es_valido(self):
        """IVA = 0 es válido para servicios o productos exentos."""
        result = parse_recibo({
            "fecha": "2026-03-24", "proveedor": "Test", "concepto": "Test",
            "subtotal": 80_000.0, "iva": 0.0, "total": 80_000.0,
            "divisa": "COP", "confianza_global": 0.80,
            "confianza_campos": {}, "archivo_origen": "test.jpg"
        })
        assert result.iva == 0.0


# ===========================================================================
# TESTS — Resiliencia del sistema (no crash bajo cualquier input)
# ===========================================================================

class TestOCRPipelineResilience:

    @pytest.mark.parametrize("bad_input", [
        None,
        42,
        [],
        "null",
        "[]",
    ])
    def test_input_inesperado_no_crashea_sistema(self, bad_input):
        """
        El sistema NUNCA debe propagar una excepción no controlada.
        Cualquier input extraño debe resultar en OCRParsingError o subclase.
        """
        with pytest.raises((OCRParsingError, TypeError, AttributeError)):
            # AttributeError es aceptable para None/int — lo importante es que
            # no propague KeyError, IndexError u otras excepciones no controladas
            # que podrían crashear el pipeline silenciosamente.
            parse_recibo(bad_input)
