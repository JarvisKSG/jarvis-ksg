# META-002 — Self-Reflection Loop: Autocrítica Interna del Enjambre
**Modulo:** JARVIS-CORE-ULTRA
**Version:** 1.0 | **Fecha:** 2026-03-24
**Propietario:** Jarvis (orquestador) + `ai_engineer` (Amendment Pipeline para cambios estructurales)
**Estado:** EN DESARROLLO
**Dependencias:** META-001 v1 estable, PERF-001 (`diagnostico_v1.md`), PR-001 (`refactor_v1.md`), SEC-001 (pendiente formalización)

---

## Principio Rector

> **"Un error que se detecta internamente cuesta cero. Un error que llega a Thomas cuesta tiempo, confianza y un ciclo QC. Un error que llega a Jeff cuesta la relación."**

META-002 introduce un paso de crítica silenciosa **entre** la entrega del subagente y la validación de QC. No reemplaza a QC — lo pre-filtra. El objetivo es que QC reciba outputs limpios y opere como verificador de alto nivel, no como cazador de errores básicos.

---

## Posición en el Flujo

```
[Thomas pide algo]
       ↓
[Agente X ejecuta su tarea]
       ↓
[META-002 — Self-Reflection] ← NUEVO (silencioso, invisible a Thomas)
       ↓
  ¿Pasa la crítica?
  /             \
SÍ               NO
 ↓                ↓
[QC]         [Internal Ticket → Agente X corrige]
 ↓                ↓
[Thomas]     [Re-ejecuta META-002 — max 2 intentos internos]
                  ↓
             [Si sigue fallando → escala a QC con ticket adjunto]
```

**Regla clave:** META-002 ocurre **antes** de QC. Si META-002 detecta y corrige un error, QC nunca lo ve. Si META-002 no puede resolverlo en 2 intentos internos, lo pasa a QC con el Internal Ticket ya adjunto para que QC tenga contexto completo.

---

## Los Tres Lentes de Crítica

### Lente 1 — PERF-001: Rendimiento

**Fuente de criterios:** `agentes/performance_engineer/diagnostico_v1.md`
**Agentes que lo aplican obligatoriamente:** `python_developer`, `api_backend`, `frontend_engineer`
**Agentes que lo aplican si su output toca el critical path:** cualquier agente que genere código

| Criterio | Verificación | Severidad |
|----------|-------------|-----------|
| OCR sincrono | ¿Hay llamada OCR sin `run_in_executor` o `asyncio`? | CRITICA |
| Sin cache en endpoints KPI | ¿El endpoint devuelve datos sin TTL cache? | ALTA |
| Model reload en cada llamada | ¿Se instancia el modelo OCR dentro del request handler? | MEDIA |
| Query sin indice a Sheets | ¿Hay lectura de rango completo en lugar de query especifica? | MEDIA |
| SLA target superado | ¿El componente supera su SLA del critical path? | ALTA |

**Accion al detectar:** Internal Ticket con patron de fix especifico del `diagnostico_v1.md`.

---

### Lente 2 — SEC-001: Seguridad

**Fuente de criterios:** `agentes/security_auditor/role.md` (secciones 2A–2E)
**Fuente de criterios:** `docs/architecture/sec-001-standards.md` — ACTIVO desde 2026-03-24.
**Agentes que lo aplican obligatoriamente:** `python_developer`, `api_backend`, `n8n_engineer`, `email_manager`

| Criterio | Verificación | Severidad |
|----------|-------------|-----------|
| Secretos hardcodeados | ¿Hay API keys, tokens o passwords en el código? | CRITICA — bloqueo inmediato |
| SQL no parametrizado | ¿Hay f-strings o concatenacion en queries SQL? | CRITICA |
| Stack trace expuesto | ¿Los errores HTTP devuelven traceback de Python? | ALTA |
| Prompt injection posible | ¿Se pasa input de usuario directamente a un prompt sin sanitizar? | ALTA |
| Secretos en `.gitignore` | ¿El archivo nuevo deberia estar en `.gitignore` y no lo esta? | ALTA |
| Bearer token cacheado | ¿Se almacena un token de autenticacion en cache compartida? | ALTA |

**Accion al detectar CRITICA:** Internal Ticket + bloqueo — el output no avanza ni a QC hasta resolverse.

---

### Lente 3 — PR-001: Claridad de Prompts y Documentación

**Fuente de criterios:** `agentes/prompt_engineer/refactor_v1.md`
**Agentes que lo aplican obligatoriamente:** cualquier agente que produzca un `role.md`, documento de arquitectura, o instruccion a otro agente

| Criterio | Verificación | Severidad |
|----------|-------------|-----------|
| Meta-instrucciones redundantes | ¿Hay "Read this file completely before..."? | BAJA |
| Emojis en reglas operativas | ¿Hay 🔴🟠🟡 en tablas de reglas? | BAJA |
| Regla QC duplicada | ¿Aparece la regla de 3 ciclos en lugar de puntero a CLAUDE.md? | MEDIA |
| Hedging innecesario | ¿Hay "At minimum", "Make sure to", "It is important that"? | BAJA |
| Etiqueta INNEGOCIABLE o similar | ¿Hay mayusculas de enfasis en etiquetas de seccion? | BAJA |
| Contexto duplicado de CLAUDE.md | ¿Se repite informacion que ya esta en el global config? | MEDIA |

---

## Formato del Internal Ticket

Cuando META-002 detecta un fallo, genera un Internal Ticket estructurado que se entrega al agente responsable:

```json
{
  "ticket_id": "IT-[AGENTE]-[YYYYMMDD]-[NNN]",
  "timestamp": "ISO 8601",
  "from": "meta_002_reflection",
  "to": "[nombre_agente]",
  "lente": "PERF-001 | SEC-001 | PR-001",
  "severidad": "CRITICA | ALTA | MEDIA | BAJA",
  "criterio_violado": "[nombre del criterio de la tabla correspondiente]",
  "ubicacion": "[archivo:linea o seccion especifica]",
  "descripcion": "[descripcion exacta del problema — sin hedging]",
  "accion_requerida": "[que debe hacer el agente para resolverlo]",
  "referencia": "[path al documento fuente del criterio]",
  "bloquea_avance": true | false
}
```

**Ejemplo real:**
```json
{
  "ticket_id": "IT-python_developer-20260324-001",
  "timestamp": "2026-03-24T10:30:00Z",
  "from": "meta_002_reflection",
  "to": "python_developer",
  "lente": "PERF-001",
  "severidad": "CRITICA",
  "criterio_violado": "OCR sincrono",
  "ubicacion": "agentes/contador/tools/extractor_recibos.py:87",
  "descripcion": "Llamada a paddle_ocr.ocr() ejecutada sincrona en el request handler. Bloquea el event loop.",
  "accion_requerida": "Envolver en asyncio.get_event_loop().run_in_executor(None, paddle_ocr.ocr, img_path)",
  "referencia": "agentes/performance_engineer/diagnostico_v1.md — PERF-BUG-001",
  "bloquea_avance": true
}
```

---

## Metricas en agent_performance.json

Cada agente que pasa por META-002 acumula metricas en su entrada de `core/memory/agent_performance.json`:

```json
"reflection_metrics": {
  "total_outputs_reflected": 0,
  "tickets_issued": 0,
  "tickets_resolved_internally": 0,
  "tickets_escalated_to_qc": 0,
  "filtration_rate_pct": 0.0,
  "last_ticket_id": null,
  "tickets_by_lente": {
    "PERF-001": 0,
    "SEC-001": 0,
    "PR-001": 0
  }
}
```

**Metrica clave — `filtration_rate_pct`:**
```
filtration_rate = (tickets_resolved_internally / tickets_issued) × 100
```
- `>= 80%` : META-002 funcionando — la mayoria de errores se filtran antes de QC
- `50-79%` : Aceptable — algunos errores llegan a QC pero con contexto del ticket
- `< 50%`  : META-002 no esta detectando correctamente — revisar criterios

**Metrica de salud del enjambre — `swarm_error_funnel`** (calculado por `performance_engineer`):
```
Errores generados → Filtrados por META-002 → Llegados a QC → Llegados a Thomas
```
El objetivo es que Thomas vea cero errores de Lente SEC-001 CRITICA y < 5% de errores de Lente PERF-001.

---

## Protocolo de Activación por Agente

META-002 se activa en dos modalidades:

### Modalidad A — Integrada (default para agentes con outputs de codigo)

El agente ejecuta la autocrítica como ultimo paso antes del handoff a QC. La instruccion en el role.md (seccion 3) debe incluir:

```
Antes del handoff a QC, ejecutar META-002:
1. Revisar output contra Lente [PERF-001|SEC-001|PR-001] segun tipo de output
2. Si se detecta falla CRITICA o ALTA: generar Internal Ticket y corregir antes de proceder
3. Si la correccion toma > 2 intentos: adjuntar ticket al handoff de QC
4. Registrar resultado en reflection_metrics de core/memory/agent_performance.json
```

### Modalidad B — On-Demand (para auditorias)

Jarvis puede invocar META-002 explicitamente sobre cualquier output existente:
```
[Jarvis] → META-002 sobre [archivo] usando Lente [X]
```
Util para auditorias retroactivas de codigo ya en produccion.

---

## Dependencias y Roadmap

### Dependencias para activacion completa

| Dependencia | Estado | Bloqueante |
|-------------|--------|-----------|
| META-001 v1 (memoria estable) | ACTIVO | Si |
| PERF-001 criterios (`diagnostico_v1.md`) | ACTIVO | Si |
| PR-001 criterios (`refactor_v1.md`) | ACTIVO | Si |
| SEC-001 formalizado (`sec-001-standards.md`) | **ACTIVO** | Desbloqueado — `security_engineer` activado 2026-03-24 |
| `agent_performance.json` con `reflection_metrics` | PENDIENTE | Si — requiere schema update |

### Roadmap META-002 → META-003

| Fase | Descripcion | Estado |
|------|-------------|--------|
| META-002 v1 (hoy) | Protocolo definido, activacion manual por Jarvis, Internal Ticket manual | EN DESARROLLO |
| META-002 v2 | Instruccion integrada en role.md de 5 agentes criticos (python_developer, api_backend, frontend_engineer, email_manager, n8n_engineer) | **DESBLOQUEADO** — SEC-001 activo, Amendment Pipeline listo |
| META-002 v3 | `reflection_metrics` en `agent_performance.json` para todos los agentes — dashboard de filtration rate | Pendiente META-003 |
| META-003 | Los tickets resueltos internamente alimentan `shared_knowledge.json` — el aprendizaje de un agente se comparte automaticamente | Pendiente META-002 v2 estable |

---

## Lo que META-002 NO es

- No reemplaza a QC — QC sigue siendo obligatorio
- No es un agente separado — es un protocolo que corre dentro del contexto del agente ejecutor
- No audita decisiones de negocio — solo criterios tecnicos de PERF/SEC/PR
- No bloquea outputs de bajo riesgo (documentacion sin codigo, reportes de texto) — Lente PR-001 en BAJA severidad no bloquea

---

*Documento: `docs/architecture/meta-002-reflection.md` | Propietario: Jarvis | Pendiente: schema update `agent_performance.json` + integracion en 5 role.md criticos*
