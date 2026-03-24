# PERF-001 — Diagnostico v1: Mapa de Calor del Sistema Keystone
**Agente:** `performance_engineer`
**Fecha:** 2026-03-24
**Metodo:** Analisis estatico del codigo + estimaciones de latencia por tipo de operacion
**Estado:** Baseline inicial — latencias estimadas, pendiente medicion real con instrumentacion

---

## Critical Path Completo — Vista General

```
FOTO RECIBO (usuario sube imagen)
        │
        ▼
┌───────────────────────┐
│  1. Upload imagen     │  ~200ms (red local) / ~800ms (4G)
│  python_developer     │  [I/O-bound — red]
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  2. OCR Processing    │  ⚠ ~2,500ms (Tesseract) / ~800ms (PaddleOCR)
│  python_developer     │  [CPU-bound — cuello de botella #1]
│  Tesseract/PaddleOCR  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  3. parse_recibo()    │  ~30ms
│  python_developer     │  [CPU-bound ligero — OK]
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  4. Sheets API write  │  ⚠ ~600ms (latencia Google API)
│  contador / Drive     │  [I/O-bound — cuello de botella #2]
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  5. FastAPI refresh   │  ~80ms (lectura Sheets en cache)
│  api_backend          │  [OK si hay cache de datos]
│                       │  ⚠ ~700ms (sin cache, re-lee Sheets)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  6. React fetch       │  ~150ms (localhost) / ~300ms (cloud)
│  frontend_engineer    │  [I/O-bound — OK]
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  7. PWA SWR cache     │  ~50ms (Stale-While-Revalidate)
│  mobile_pwa           │  [OK — diseno correcto]
└───────────┬───────────┘
            │
            ▼
  iPhone Jeff ve KPI actualizado
```

**Total estimado (Tesseract, sin cache API):** ~4,310ms — SUPERA SLA cloud (6,000ms: OK · local: CRITICO)
**Total estimado (PaddleOCR, con cache API):** ~1,810ms — DENTRO DE SLA ✅

---

## Mapa de Calor por Etapa

| # | Etapa | Responsable | Latencia Estimada | Tipo | Severidad | SLA 800ms |
|---|-------|-------------|-------------------|------|-----------|-----------|
| 1 | Upload imagen | `python_developer` | 200ms (local) | I/O red | OK | PASS |
| 2 | OCR Tesseract | `python_developer` | ~2,500ms | CPU-bound | **CRITICO** | **FAIL** |
| 2b | OCR PaddleOCR | `python_developer` | ~800ms | CPU-bound | WARN | BORDERLINE |
| 3 | parse_recibo() | `python_developer` | ~30ms | CPU ligero | OK | PASS |
| 4 | Sheets API write | `contador` / Drive | ~600ms | I/O API | WARN | PASS |
| 4b | Sheets API (pico) | `contador` / Drive | ~1,200ms | I/O API | **BUG** | **FAIL** |
| 5 | FastAPI (con cache) | `api_backend` | ~80ms | CPU/cache | OK | PASS |
| 5b | FastAPI (sin cache) | `api_backend` | ~700ms | I/O API | WARN | PASS |
| 6 | React fetch + render | `frontend_engineer` | ~150ms | I/O red | OK | PASS |
| 7 | PWA SWR hit | `mobile_pwa` | ~50ms | cache | OK | PASS |

---

## Top 3 Cuellos de Botella — Prioridad de Optimizacion

### [PERF-BUG-001] OCR Sincrono bloquea hilo principal — CRITICO

**Etapa:** OCR Processing (etapa 2)
**Latencia actual:** ~2,500ms (Tesseract) · ~800ms (PaddleOCR)
**Tipo:** CPU-bound, sincrono — bloquea el event loop de FastAPI mientras procesa
**Impacto:** Cada upload de recibo paralelo encola atras del anterior. Con 3 recibos simultaneos: 3× latencia.

**Root cause:**
```python
# Patron actual (BLOQUEANTE):
def process_receipt(image_path: str) -> ReciboExtraido:
    text = pytesseract.image_to_string(image_path)  # Bloquea el hilo 2,500ms
    return parse_recibo(text)

# Patron recomendado (NO BLOQUEANTE):
async def process_receipt(image_path: str) -> ReciboExtraido:
    text = await asyncio.get_event_loop().run_in_executor(
        None,  # ThreadPoolExecutor por defecto
        pytesseract.image_to_string,
        image_path
    )
    return parse_recibo(text)
```

**Fix recomendado:**
1. Migrar `process_receipt()` a `async` con `run_in_executor` (ThreadPool para CPU-bound)
2. Migrar de Tesseract a PaddleOCR 3.x (RES-001 ya documento: CER 8% vs 25.4%, 3× mas rapido)
3. Latencia proyectada post-fix: ~800ms (PaddleOCR async) → **dentro del SLA**

**Responsable implementacion:** `python_developer`
**Tests requeridos:** `tester_automation` debe agregar prueba de concurrencia (3 uploads simultaneos)

---

### [PERF-BUG-002] Google Sheets API sin cache de lectura — BUG

**Etapa:** FastAPI re-lee Sheets en cada request (etapa 5b)
**Latencia actual:** ~700ms por request al endpoint `/api/v1/dashboard/health` sin cache
**Tipo:** I/O-bound — llamada HTTP a Google Sheets API en cada request del dashboard

**Root cause:**
Cada vez que React hace fetch al dashboard, FastAPI llama a Google Sheets para leer los datos. Con Jeff recargando en movil cada 30 segundos: 2 llamadas/minuto × 700ms = latencia innecesaria.

**Fix recomendado:**
```python
# En api_backend — agregar cache en memoria con TTL
from functools import lru_cache
import time

_kpi_cache = {"data": None, "timestamp": 0}
KPI_CACHE_TTL = 300  # 5 minutos — alineado con Service Worker de mobile_pwa

async def get_kpis_nivel1() -> dict:
    now = time.time()
    if _kpi_cache["data"] and (now - _kpi_cache["timestamp"]) < KPI_CACHE_TTL:
        return _kpi_cache["data"]  # Cache hit: ~5ms

    data = await fetch_from_sheets()  # Cache miss: ~600ms
    _kpi_cache.update({"data": data, "timestamp": now})
    return data
```

**Latencia proyectada post-fix:** ~5ms (cache hit, 95% de los requests) · ~600ms (cache miss, refresh)
**Responsable:** `api_backend`
**Coordinacion:** `mobile_pwa` — alinear TTL cache (ambos en 5 minutos)

---

### [PERF-WARN-001] Carga de modelo OCR en cada request — WARN

**Etapa:** OCR Processing — inicializacion del modelo
**Latencia adicional:** ~400ms extra en el primer request tras reinicio del servidor
**Tipo:** CPU/Memory-bound — carga del modelo Tesseract/PaddleOCR en memoria

**Fix recomendado:**
```python
# Pattern Singleton — cargar modelo una vez al arrancar el servidor
class OCREngine:
    _instance = None
    _model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._model = cls._load_model()  # Solo una vez al arrancar
        return cls._instance

# En FastAPI startup event:
@app.on_event("startup")
async def startup():
    OCREngine.get_instance()  # Pre-carga el modelo
```

**Latencia proyectada:** Primer request: 400ms → ~50ms (modelo ya en memoria)
**Responsable:** `python_developer`

---

## Auditoria de Consultas — Caja Negra (Google Sheets)

Google Sheets no tiene indices tradicionales como SQL. Los patrones de acceso mas costosos son:

| Query pattern | Costo actual | Optimizacion recomendada |
|--------------|-------------|--------------------------|
| Leer todas las filas de una hoja mensual | O(n) scan | Usar columna ID Unico como lookup, paginar con `range` |
| Filtrar por categoria (OP/MF/PROY) | Scan completo | Cache en memoria por categoria (TTL 5 min) con invalidacion on-write |
| Calcular totales para KPIs | Suma en Python sobre todas las filas | Usar formula `=SUMIF()` nativa de Sheets — Google la ejecuta server-side |
| Top 3 proveedores por gasto | Sort + slice en Python | Pre-calcular en hoja `DASHBOARD_ANUAL` via formula, FastAPI solo lee 1 celda |

**Recomendacion general:** Las formulas nativas de Google Sheets (`SUMIF`, `QUERY`, `SORT`) son ejecutadas por los servidores de Google y son significativamente mas rapidas que traer todos los datos a Python y calcular ahi. `database_architect` deberia auditar que todos los KPIs del `data_scientist` esten pre-calculados en `DASHBOARD_ANUAL`.

---

## Roadmap de Optimizacion

| Prioridad | Fix | Agente | Impacto estimado | Esfuerzo |
|-----------|-----|--------|-----------------|----------|
| 1 | Migrar OCR a async + PaddleOCR | `python_developer` | -1,700ms (Tesseract→PaddleOCR async) | Alto |
| 2 | Cache en memoria para KPIs FastAPI | `api_backend` | -665ms (cache hit 95%) | Bajo |
| 3 | Singleton OCR model preload | `python_developer` | -350ms (cold start) | Bajo |
| 4 | Pre-calcular KPIs en DASHBOARD_ANUAL | `database_architect` | -200ms (elimina SUMIF en Python) | Medio |
| 5 | Lighthouse Performance >= 90 | `frontend_engineer` | UX Jeff mejora | Medio |

**Ganancia total proyectada (todos los fixes):** ~2,915ms → Critical Path estimado: **~1,395ms** (local) ✅

---

## Proximos Pasos PERF-001

- [ ] Instrumentar con `@timed` decorator las etapas 2, 3, 4 en produccion para medir latencias reales
- [ ] Validar latencia real de Sheets API (puede variar 300ms–1,200ms segun carga de Google)
- [ ] Coordinar con `python_developer`: PERF-BUG-001 (async OCR)
- [ ] Coordinar con `api_backend`: PERF-BUG-002 (cache KPIs)
- [ ] Crear PERF-002: benchmark de concurrencia (simular 5 uploads simultaneos con locust)

---

*Generado por: `performance_engineer` | Pendiente: medicion real con instrumentacion | Validacion: `qc`*
