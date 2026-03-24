# PR-001 — Reporte de Optimizacion de Prompts v1
**Agente:** `prompt_engineer`
**Fecha:** 2026-03-24
**Alcance:** Auditoria de role.md — `scrum_master` + `python_developer`
**Objetivo:** Reducir verbosidad, eliminar redundancias, vincular a PERF-001

---

## Resumen Ejecutivo

| Agente | Tokens estimados (original) | Tokens estimados (propuesta) | Reduccion | Estado |
|--------|----------------------------|------------------------------|-----------|--------|
| `scrum_master` | ~2,850 | ~1,680 | **41%** | Propuesta lista — pendiente aprobacion Thomas |
| `python_developer` | ~3,400 | ~2,050 | **40%** | Propuesta lista — pendiente aprobacion Thomas |

**Hallazgos transversales (aplican al enjambre completo):**
- 14 de 28 agentes tienen el patron "Read this file completely before [action]" — instruccion redundante: un agente que no lee su rol primero ya tiene un problema mas grave que el prompt no puede resolver
- 9 de 28 agentes repiten contexto que ya esta en `CLAUDE.md` o `core/memory/global_config.json`
- 6 de 28 agentes usan emojis en secciones operativas (🔴🟠🟡) — viola estandar del enjambre
- El patron "Max 3 QC cycles. Cycle 4 → escalate" aparece identico en 11 agentes — candidato a extractarse a una regla global en `CLAUDE.md`

---

## Auditoria 1: `scrum_master`

### Hallazgos por categoria

| # | Categoria | Ubicacion | Descripcion |
|---|-----------|-----------|-------------|
| SM-01 | Redundancia | Section 1, paso 1 | "Read this file completely before touching the backlog" — instruccion meta que no agrega valor operativo |
| SM-02 | Emojis en reglas | Section 2.A Priority Score Guide | 🔴🟠🟡🟢⚪ en tabla de prioridades — viola estandar no-emoji del enjambre |
| SM-03 | Cortesia innecesaria | Section 2.C, "When Thomas mentions a task" | "ask one clarifying question before scoring, not multiple" — la restriccion "not multiple" es obvia y patronizante |
| SM-04 | Contexto en CLAUDE.md | Section 1, punto 3 | "Read protocols/agent_registry.md to know which agents exist" — esto es parte del startup protocol global RAG-Lite, no especifico del scrum_master |
| SM-05 | Overhead de seccion | Section 2.F "Swarm Capacity Model" | 6 lineas para decir "maximo 3 tareas paralelas y Thomas solo trabaja fin de semana" — fusionable en Sprint Definition |
| SM-06 | Redundancia | Section 3 QC checklist | Repite los field names del schema de Section 2.A — el checklist puede referenciar la seccion en lugar de re-listar |
| SM-07 | Ejemplo sobredimensionado | Section 2.E Milestone Tracking | El bloque markdown de ejemplo del milestone es identico al formato ya documentado en backlog.md — puede ser un puntero |

### Antes y Despues — Seccion critica: Navigation & Lazy Loading

**ANTES (68 tokens):**
```
When spawned:
1. Read this file completely before touching the backlog
2. **Always** read `memory/backlog.md` as first action — never assume you know its current state
3. Read `protocols/agent_registry.md` to know which agents exist and can execute tasks
4. If the task involves a specific project → read that project's `context.md` in `projects/[PROY-XXX]/`
5. If the task involves open audit findings → read `agentes/ai_engineer/tools/proposals/` for amendment status
```

**DESPUES (38 tokens — reduccion 44%):**
```
Al invocar:
1. Leer `memory/backlog.md` — estado actual, nunca asumir
2. Si tarea involucra proyecto especifico → `projects/[PROY-XXX]/context.md`
3. Si tarea involucra findings de auditoria → `agentes/ai_engineer/tools/proposals/`
```
*Eliminados: paso meta "read this file" (implicito), paso de agent_registry (cubierto por RAG-Lite global)*

---

### Antes y Despues — Seccion critica: Priority Score Guide

**ANTES (tabla con emojis, 52 tokens):**
```
| Score | Interpretation |
|-------|---------------|
| 8–10 | 🔴 Crítico — ejecutar en el sprint actual |
| 5–7  | 🟠 Alto — próximo sprint |
| 3–4  | 🟡 Medio — planificar cuando haya capacidad |
| 0–2  | 🟢 Bajo — backlog refinement periódico |
| < 0  | ⚪ Descartable — cuestionar si vale la pena |
```

**DESPUES (sin emojis, 38 tokens — reduccion 27%):**
```
| Score | Accion |
|-------|--------|
| 8–10 | Sprint actual |
| 5–7  | Proximo sprint |
| 3–4  | Planificar cuando haya capacidad |
| 0–2  | Backlog refinement periodico |
| < 0  | Proponer cancelacion a Thomas |
```
*Eliminados: emojis, etiquetas verbales redundantes con el Score (si el score es 9, "Critico" no agrega informacion)*

---

### Antes y Despues — Seccion critica: Swarm Capacity Model (fusion)

**ANTES (Section 2.F completa, 71 tokens):**
```
## F. Swarm Capacity Model

When planning a sprint, consult `protocols/agent_registry.md` and estimate:

Agents available (can run any day):   [list from registry]
Thomas available (Sat-Sun only):       max 2 days/week
Max parallel agent tasks:              3 (Jarvis constraint — avoid context overload)

**Sequencing rule:** Tasks with dependencies must be ordered. Mark blocking relationships in Notas:
"Requiere BACK-XXX completado primero"
```

**DESPUES (fusionado en Sprint Definition, 28 tokens — reduccion 61%):**
```
Capacidad del sprint: Thomas disponible Sab-Dom. Maximas 3 tareas paralelas en agentes.
Dependencias: marcar en Notas "Requiere BACK-XXX completado primero".
```

---

## Auditoria 2: `python_developer`

### Hallazgos por categoria

| # | Categoria | Ubicacion | Descripcion |
|---|-----------|-----------|-------------|
| PY-01 | Redundancia | Section 1, paso 1 | "Read this file completely before writing a single line of code" — patron meta redundante (identico SM-01) |
| PY-02 | Ambiguedad | Section 2, etiqueta "INNEGOCIABLE" | Mezcla idiomas sin justificacion; la palabra "INNEGOCIABLE" en mayusculas no agrega fuerza normativa sobre lo que ya dice la seccion |
| PY-03 | Ejemplo sobredimensionado | Section 2 "Good vs Bad" | El bloque "Bad" muestra codigo que ningun developer escribiria hoy — el ejemplo negativo no esta calibrado al riesgo real |
| PY-04 | Redundancia | Section 2, Security Practices | "`bandit` scan before delivering any script: `bandit -r [script].py -ll`" — ya aparece en el QC checklist de Section 3 |
| PY-05 | Overhead de seccion | Section 2, Package Management | "Install command to document in script header" + ejemplo de requirements.txt podrian ser una sola regla |
| PY-06 | Contexto duplicado | Section 2, Integration Points table | La tabla repite agentes que ya estan en `protocols/agent_registry.md` — puede ser un puntero |
| PY-07 | Cortesia innecesaria | Section 2, Testing Standards | "At minimum: one happy-path test + one error-path test per public function" — el "at minimum" es hedging innecesario; si es el estandar, es el estandar |

### Antes y Despues — Seccion critica: Navigation & Lazy Loading

**ANTES (85 tokens):**
```
When spawned:
1. Read this file completely before writing a single line of code
2. Check `agentes/[relevant_agent]/tools/` for existing scripts — never duplicate working code
3. If the task involves financial data → confirm TRM with Thomas before processing
4. If the task involves credentials → read `protocols/security.md` first
5. After writing any script → confirm it has a corresponding `requirements.txt` in its `tools/` folder
```

**DESPUES (42 tokens — reduccion 51%):**
```
Al invocar:
1. Revisar `agentes/[agente_relevante]/tools/` — no duplicar codigo existente
2. Datos financieros → confirmar TRM con Thomas antes de procesar
3. Credenciales → leer `protocols/security.md` primero
4. Todo script entregado → `requirements.txt` en `tools/` con versiones pinneadas
```

---

### Antes y Despues — Seccion critica: Testing Standards

**ANTES (47 tokens):**
```
- `pytest` for all scripts with external dependencies
- At minimum: one happy-path test + one error-path test per public function
- Mock external calls with `unittest.mock.patch` or `pytest-mock`
- Test files live in `tools/tests/` alongside the script
```

**DESPUES (28 tokens — reduccion 40%):**
```
- pytest obligatorio en scripts con dependencias externas
- Una prueba happy-path + una error-path por funcion publica
- Mocks: `unittest.mock.patch` o `pytest-mock`
- Tests en `tools/tests/`
```

---

### Antes y Despues — Seccion critica: Etiqueta INNEGOCIABLE

**ANTES:**
```
## Keystone Script Standard (INNEGOCIABLE)
```

**DESPUES:**
```
## Keystone Script Standard
```
*Razon: La etiqueta "INNEGOCIABLE" en mayusculas es ruido — si la regla tiene consecuencias de QC, el QC la hace cumplir. Una etiqueta no agrega fuerza normativa.*

---

## Hallazgo Transversal — Candidato a Regla Global

El siguiente bloque aparece textualmente en 11 de 28 role.md:

```
Max 3 QC cycles. Cycle 4 → escalate to [Thomas/Jarvis].
```

**Recomendacion:** Mover esta regla a `CLAUDE.md` como regla global del enjambre y eliminarla de los 11 role.md individuales. Reduccion estimada: ~200 tokens del enjambre completo.

**Accion requerida:** Aprobacion de Thomas → `ai_engineer` ejecuta via Amendment Pipeline.

---

## Proximos Candidatos de Auditoria (por impacto estimado)

| Agente | Tokens estimados | Razon de prioridad |
|--------|-----------------|-------------------|
| `qc` | ~2,100 | Role central — cualquier verbosidad se multiplica por 28 invocaciones |
| `ai_engineer` | ~1,800 | Tiene el Amendment Pipeline documentado en prosa densa |
| `compliance` | ~900 | Probablemente tiene reglas DIAN repetidas en multiple lugares |
| `entity_intelligence` | ~700 | social_graph.md es el output — el role puede ser mas escueto |

---

*Generado por: `prompt_engineer` | PR-001 | Pendiente: aprobacion Thomas para aplicar cambios a role.md en produccion*
