"""
trm_sync.py — Keystone KSG TRM Fetcher
Agente: localization_expert
Version: 1.0 | Fecha: 2026-03-24

Consulta la Tasa Representativa del Mercado (TRM) oficial del Banco de la Republica
de Colombia via la API de datos.gov.co (SOCRATA) y la registra en Caja Negra.

Uso:
    python trm_sync.py               # Muestra TRM de hoy
    python trm_sync.py --date 2026-03-20  # TRM de una fecha especifica
    python trm_sync.py --convert 1000000  # Convierte 1,000,000 COP a USD
    python trm_sync.py --history 7   # Muestra ultimos 7 dias de TRM

Fuente oficial: Banco de la Republica de Colombia
API: https://www.datos.gov.co/resource/mcec-87by.json (dataset TRM)
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

# API publica de datos.gov.co — no requiere credenciales para lectura basica
TRM_API_URL = "https://www.datos.gov.co/resource/mcec-87by.json"
TRM_CACHE_FILE = Path(__file__).parent / "trm_cache.json"

# TRM de fallback si la API no responde (actualizar manualmente si es necesario)
TRM_FALLBACK = {
    "valor": 4200.0,
    "fecha": "2026-03-24",
    "fuente": "FALLBACK_MANUAL — actualizar con valor real de banrep.gov.co"
}


# ---------------------------------------------------------------------------
# Fetch TRM
# ---------------------------------------------------------------------------

def fetch_trm(for_date: date = None) -> dict:
    """
    Obtiene la TRM oficial del Banco de la Republica.
    Si for_date es None, retorna la TRM vigente hoy.
    Retorna dict con: valor (float), fecha (str), fuente (str).
    """
    if for_date is None:
        for_date = date.today()

    date_str = for_date.strftime("%Y-%m-%d")

    # Construir query SOCRATA: TRM vigente en la fecha solicitada
    # vigenciadesde <= fecha AND vigenciahasta >= fecha
    params = {
        "$where": f"vigenciadesde <= '{date_str}T00:00:00' AND vigenciahasta >= '{date_str}T00:00:00'",
        "$order": "vigenciadesde DESC",
        "$limit": "1"
    }

    url = f"{TRM_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "Keystone-KSG-localization_expert/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data:
            # Intentar con fecha un dia anterior (TRM puede no estar publicada aun hoy)
            if for_date == date.today():
                return fetch_trm(for_date - timedelta(days=1))
            raise ValueError(f"No se encontro TRM para {date_str}")

        record = data[0]
        valor = float(record.get("valor", 0))
        vigencia = record.get("vigenciadesde", date_str)[:10]

        result = {
            "valor": round(valor, 2),
            "fecha": vigencia,
            "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fuente": "Banco de la Republica / datos.gov.co",
            "vigencia_desde": record.get("vigenciadesde", "")[:10],
            "vigencia_hasta": record.get("vigenciahasta", "")[:10]
        }

        _update_cache(result)
        return result

    except Exception as e:
        print(f"[LOC-WARN] No se pudo conectar a API TRM: {e}")
        print("[LOC-WARN] Usando valor de cache o fallback...")
        return _get_cached_trm(date_str)


def _get_cached_trm(date_str: str) -> dict:
    """Retorna TRM desde cache local. Si no existe, retorna el fallback."""
    if TRM_CACHE_FILE.exists():
        with open(TRM_CACHE_FILE) as f:
            cache = json.load(f)
        if date_str in cache:
            cached = cache[date_str].copy()
            cached["fuente"] += " [CACHE LOCAL]"
            return cached
        # Retornar el mas reciente disponible
        if cache:
            latest_key = sorted(cache.keys())[-1]
            latest = cache[latest_key].copy()
            latest["fuente"] += f" [CACHE LOCAL — mas reciente disponible: {latest_key}]"
            return latest

    return TRM_FALLBACK.copy()


def _update_cache(trm_data: dict) -> None:
    """Actualiza el cache local de TRM."""
    cache = {}
    if TRM_CACHE_FILE.exists():
        with open(TRM_CACHE_FILE) as f:
            cache = json.load(f)

    cache[trm_data["fecha"]] = trm_data

    # Mantener solo los ultimos 90 dias en cache
    if len(cache) > 90:
        sorted_keys = sorted(cache.keys())
        for old_key in sorted_keys[:-90]:
            del cache[old_key]

    with open(TRM_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def cop_to_usd(amount_cop: float, trm: float = None) -> dict:
    """Convierte COP a USD usando la TRM del dia."""
    if trm is None:
        trm_data = fetch_trm()
        trm = trm_data["valor"]
        trm_date = trm_data["fecha"]
    else:
        trm_date = "proporcionado"

    usd = round(amount_cop / trm, 2)
    return {
        "cop": amount_cop,
        "usd": usd,
        "trm": trm,
        "trm_fecha": trm_date,
        "formula": f"{amount_cop:,.0f} COP / {trm:,.2f} = ${usd:,.2f} USD"
    }


def usd_to_cop(amount_usd: float, trm: float = None) -> dict:
    """Convierte USD a COP usando la TRM del dia."""
    if trm is None:
        trm_data = fetch_trm()
        trm = trm_data["valor"]
        trm_date = trm_data["fecha"]
    else:
        trm_date = "proporcionado"

    cop = round(amount_usd * trm, 0)
    return {
        "usd": amount_usd,
        "cop": cop,
        "trm": trm,
        "trm_fecha": trm_date,
        "formula": f"${amount_usd:,.2f} USD × {trm:,.2f} = {cop:,.0f} COP"
    }


def format_dual_currency(amount_cop: float, trm_data: dict = None) -> str:
    """
    Formatea una cantidad COP con su equivalente USD.
    Formato estandar Keystone: '$8,245,000 COP (~$1,963 USD @ TRM $4,200)'
    """
    if trm_data is None:
        trm_data = fetch_trm()

    trm = trm_data["valor"]
    usd = amount_cop / trm
    return f"${amount_cop:,.0f} COP (~${usd:,.0f} USD @ TRM ${trm:,.0f})"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Keystone KSG TRM Sync — localization_expert",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--date", help="Fecha especifica YYYY-MM-DD (default: hoy)")
    parser.add_argument("--convert", type=float, help="Convierte N pesos COP a USD")
    parser.add_argument("--history", type=int, default=0, metavar="N",
                        help="Muestra los ultimos N dias de TRM")
    args = parser.parse_args()

    if args.history > 0:
        print(f"TRM — ultimos {args.history} dias:")
        print(f"{'Fecha':<12} {'TRM (COP/USD)':>15} {'Fuente'}")
        print("-" * 55)
        for i in range(args.history - 1, -1, -1):
            d = date.today() - timedelta(days=i)
            trm = fetch_trm(d)
            print(f"{trm['fecha']:<12} {trm['valor']:>15,.2f}  {trm['fuente'][:30]}")
        return

    target_date = date.fromisoformat(args.date) if args.date else None
    trm_data = fetch_trm(target_date)

    print(f"\nTRM Keystone KSG — {trm_data['fecha']}")
    print(f"{'─' * 40}")
    print(f"  Valor:     ${trm_data['valor']:,.2f} COP/USD")
    print(f"  Vigencia:  {trm_data.get('vigencia_desde', 'N/A')} → {trm_data.get('vigencia_hasta', 'N/A')}")
    print(f"  Fuente:    {trm_data['fuente']}")
    print(f"  Consultado: {trm_data.get('fecha_consulta', 'N/A')}")

    if args.convert:
        result = cop_to_usd(args.convert, trm_data["valor"])
        print(f"\nConversion:")
        print(f"  {result['formula']}")
        print(f"\n  Formato estandar Keystone:")
        print(f"  {format_dual_currency(args.convert, trm_data)}")

    print()


if __name__ == "__main__":
    main()
