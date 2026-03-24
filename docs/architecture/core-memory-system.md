# META-001 — Long-Term Memory System: Arquitectura Jarvis Core
**Modulo:** JARVIS-CORE-ULTRA
**Version:** 1.0 | **Fecha:** 2026-03-24
**Propietario:** Jarvis (orquestador) + `ai_engineer` (Amendment Pipeline para cambios estructurales)

---

## Principio Rector — Regla de Oro

> **"La memoria debe ser atomica y veraz: si un dato cambia (ej. la TRM), el nodo correspondiente debe actualizarse en milisegundos para que todo el enjambre trabaje sobre la misma verdad."**

Un enjambre que trabaja con datos de ayer toma decisiones de ayer. Cada nodo de memoria tiene un propietario, una frecuencia de actualizacion, y una regla de invalidacion. No hay verdad compartida sin sincronizacion garantizada.

---

## Arquitectura del Sistema

```
jarvis-ksg/
└── core/
    └── memory/                          ← Fuente de verdad del enjambre (gitignored: archivos runtime)
        ├── global_config.json           ← Estandares Keystone, TRM vigente, protocolos — COMMITTED
        ├── user_preferences.md          ← Perfil Thomas, estilo de comunicacion — COMMITTED
        ├── agent_performance.json       ← Latencias y metricas de agentes — GITIGNORED (runtime)
        └── session_state.json           ← Estado de la sesion activa — GITIGNORED (efimero)

docs/
└── architecture/
    └── core-memory-system.md           ← Este archivo — COMMITTED
```

---

## Nodos de Memoria

### Nodo 1: `global_config.json` — Estandares Atomicos del Enjambre

**Proposito:** Fuente unica de verdad para constantes del sistema. Todo agente que necesite TRM, modelo por defecto, o parametro de Keystone lee de aqui — nunca asume.

**Propietario de actualizacion:**
| Campo | Propietario | Frecuencia | Invalidacion |
|-------|-------------|------------|--------------|
| `trm.valor` | `localization_expert` via `trm_sync.py` | Diario 09:00 COT | Cualquier cambio en Banco de la Republica |
| `models.default` | `ai_engineer` | Solo tras Amendment | Cambio de modelo Claude |
| `encryption.algorithm` | `security_auditor` | Solo tras auditoria | Cambio de politica de seguridad |
| `backup.retention_days` | `recovery_specialist` | Solo con aprobacion Thomas | Cambio de politica de retencion |

**Esquema:**
```json
{
  "version": "1.0",
  "last_updated": "YYYY-MM-DDTHH:MM:SSZ",
  "updated_by": "agent_name",
  "trm": { "valor": 0.0, "fecha": "", "fuente": "" },
  "models": { "default": "", "reasoning": "" },
  "encryption": { "algorithm": "", "key_length": 0 },
  "backup": { "retention_days": 0, "schedule": "" },
  "swarm": { "active_agents": 0, "version": "" }
}
```

---

### Nodo 2: `user_preferences.md` — Perfil del Director

**Proposito:** Calibrar el comportamiento de Jarvis y todos los agentes segun las preferencias documentadas de Thomas. Este nodo es el "tono de voz" del enjambre.

**Propietario:** Jarvis actualiza tras observar patrones nuevos. Thomas puede corregir directamente.

**Estructura:** Ver archivo — incluye comunicacion, estilo tecnico, restricciones, y el primer dump completo.

---

### Nodo 3: `agent_performance.json` — Registro de Latencias y Exitos (GITIGNORED)

**Proposito:** Registro en tiempo de ejecucion de metricas por agente — alimenta al `performance_engineer` y al META-002 Self-Reflection Loop.

**Propietario:** Jarvis escribe en cada interaccion. `performance_engineer` lee para analisis.

**Estructura:**
```json
{
  "schema_version": "1.0",
  "agents": {
    "agent_name": {
      "last_invoked": "ISO timestamp",
      "avg_latency_ms": 0,
      "success_count": 0,
      "failure_count": 0,
      "last_output_qc_status": "APPROVED|REJECTED|PENDING",
      "notes": ""
    }
  }
}
```

---

### Nodo 4: `session_state.json` — Estado Efimero de Sesion (GITIGNORED)

**Proposito:** Captura el estado al cierre de sesion para que la proxima inicie exactamente donde termino. Equivalente a `session_handoff.md` pero estructurado para lectura automatica.

**Propietario:** Jarvis escribe al cierre de sesion. Jarvis lee al inicio.

---

## Protocolo de Arranque RAG-Lite

Al inicio de **cada sesion**, Jarvis ejecuta este protocolo de carga de contexto en orden secuencial:

```
STARTUP SEQUENCE — Jarvis Long-Term Memory Load
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASO 1 — Identidad y Protocolos [SIEMPRE]
  └─ Leer CLAUDE.md → identidad, reglas core, indice de protocolos

PASO 2 — Contexto del Director [SIEMPRE]
  └─ Leer core/memory/user_preferences.md → estilo, restricciones, preferencias Thomas

PASO 3 — Estado del Enjambre [SIEMPRE]
  └─ Leer core/memory/global_config.json → TRM vigente, modelo activo, estandares
  └─ Leer protocols/agent_registry.md → que agentes existen y su estado

PASO 4 — Estado del Trabajo [SI HAY SESION PREVIA]
  └─ Leer session_handoff.md (si existe) → tarea en curso, contexto de continuacion
  └─ Leer core/memory/session_state.json (si existe) → estado estructurado previo

PASO 5 — Sprint Activo [SI THOMAS MENCIONA TAREAS]
  └─ Leer memory/backlog.md → sprint actual, items en curso
  └─ Leer memory/social_graph.md → si hay interaccion con Jeff/Keyser

PASO 6 — Protocolo Especifico [SEGUN CONTEXTO]
  └─ Leer protocol file segun la tarea (kaiser.md, email.md, etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tiempo objetivo de carga: < 30 segundos (lectura de archivos clave)
Estado post-carga: Jarvis conoce quien es Thomas, que hay en el enjambre, y que esta en curso
```

---

## Reglas de Actualizacion Atomica

**Regla 1 — Single Writer:**
Cada nodo tiene exactamente UN propietario que puede escribir. Dos agentes nunca escriben en el mismo nodo simultaneamente. Si hay conflicto → `qc` arbitra.

**Regla 2 — Timestamp Obligatorio:**
Todo cambio en cualquier nodo JSON debe actualizar el campo `last_updated` con timestamp UTC. Sin timestamp = sin validez.

**Regla 3 — Invalidacion Explicita:**
Si un dato cambia (TRM, modelo activo, agente nuevo), el nodo debe marcarse como `"status": "STALE"` hasta que el propietario lo actualice. Ningun agente debe usar un nodo con status STALE para decisiones criticas.

**Regla 4 — Auditabilidad:**
Los nodos COMMITTED (`global_config.json`, `user_preferences.md`) tienen historial en git. Los nodos GITIGNORED (`agent_performance.json`, `session_state.json`) son efimeros por diseno — se reconstruyen desde el enjambre si se pierden.

---

## Evolucion Planificada (META-001 → META-004)

| Fase | Descripcion | Dependencia |
|------|-------------|-------------|
| META-001 v1 (hoy) | Archivos estructurados + RAG-Lite manual | Ninguna — implementado |
| META-001 v2 | TRM auto-sync via cron + invalidacion automatica STALE | `localization_expert` cron activo |
| META-002 | Self-Reflection Loop lee `agent_performance.json` para pre-validar outputs | META-001 v1 estable |
| META-003 | Cross-Agent KT escribe en un nodo `shared_knowledge.json` que todos leen | META-001 v2 + `ai_engineer` |
| META-004 | `session_state.json` incluye contexto multimodal (audio transcripts, foto refs) | Claude multimodal + Whisper |
