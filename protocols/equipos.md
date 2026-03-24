# Protocolo — Agent Teams
**Lee este archivo cuando vayas a crear un equipo de agentes.**

## Agent Factory — Creación Dinámica de Agentes

Ejecutar **antes** del Lifecycle Completo si el proyecto requiere un experto que no existe aún.

### Paso 0: Gap Analysis

```
1. Listar carpetas existentes en agentes/
2. Verificar si algún agente cubre el dominio requerido
   └── Si existe → usar ese agente, saltar al Lifecycle Completo
   └── Si no existe → fabricar el agente (pasos 1–4 abajo)
```

### Paso 1: Crear Workspace

```
agentes/[nombre_experto]/
├── role.md        ← a generar en Paso 2
└── tools/         ← carpeta vacía, scripts específicos van aquí
```

Convención de nombres: todo minúsculas, sin espacios (ej. `n8n-expert`, `fluidos`, `data-analyst`).

### Paso 2: Generar role.md

Redactar siguiendo el estándar de la arquitectura (ver `agentes/contador/role.md` o `agentes/qc/role.md` como referencia):

```markdown
---
name: [nombre]
description: "[cuándo invocar este agente — use-case oriented]"
tools: [solo los que necesita]
model: claude-3-7-sonnet-20250219
---

# Identity & Role
Eres el especialista autónomo en [dominio] dentro del ecosistema de Keystone KSG...

# 1. Navigation & Lazy Loading
# 2. Autonomy & Execution  ← reglas específicas del dominio
# 3. Mandatory QC & Handoff
# 4. Evolution Zone
```

El system prompt debe ser riguroso y específico al dominio — no genérico. Si el dominio requiere contexto técnico (ej. n8n, mecánica de fluidos), incluir las mejores prácticas concretas en la sección 2.

### Paso 3: Registrar en KB

Añadir entrada en `memory/keystone_kb.md` bajo `## Team Evolution`:
```
## [YYYY-MM-DD] TEAM EVOLUTION: nuevo agente — [nombre]
Dominio: [descripción]
Activado por: [proyecto o tarea que lo requirió]
```

### Paso 4: Verificación antes de Spawn

- Confirmar a Thomas: "Agente `[nombre]` fabricado. Workspace en `agentes/[nombre]/`. ¿Procedo con el equipo?"
- Esperar confirmación explícita de Thomas antes de hacer spawn
- Razón: un agente nuevo no ha sido validado en producción — Thomas debe dar el visto bueno

---

## Lifecycle Completo

```
1. TeamCreate       → crear equipo con nombre descriptivo de la tarea
2. TaskCreate       → definir tasks con dependencias (qc siempre al final)
3. Agent (spawn)    → invocar teammates con team_name + name
4. TaskUpdate       → asignar tasks por nombre de teammate
5. Coordinar        → monitorear mensajes, desbloquear, facilitar P2P
6. QC Gate          → qc valida el output consolidado (C1–C7)
7. Shutdown         → SendMessage shutdown_request a cada teammate
8. Cleanup          → TeamCleanup
9. KB Update        → registrar lecciones en memory/keystone_kb.md
10. Entregar        → output aprobado por qc llega a Thomas
```

## Descomposición de Tareas

1. Dividir en unidades independientes y paralelizables
2. Cada task tiene criterios de aceptación claros en su descripción
3. Mapear dependencias con `blockedBy`
4. La task de `qc` es siempre la última — bloqueada por todas las demás
5. Un solo dueño por output — nunca dos teammates sobre el mismo entregable

## Task QC (siempre incluir)

```
TaskCreate({
  subject: "QC Validation — [nombre de la tarea]",
  description: "Revisa el output consolidado de todos los teammates. Aplica capas C1–C7. Aprueba o rechaza con acciones correctivas específicas. Ningún output sale sin tu ✅. Lee protocols/qc-capas.md para las reglas completas.",
  blockedBy: [todos los IDs anteriores]
})
```

## P2P — Comunicación entre Teammates

- Usar `SendMessage` con `to: "[nombre]"` para comunicación directa
- Usar `broadcast` solo para anuncios críticos a todo el equipo
- No enviar JSON de estado entre teammates — usar texto plano + `TaskUpdate`
- Teammates se descubren leyendo `~/.claude/teams/{team-name}/config.json`
- Siempre referirse a teammates por NOMBRE, nunca por UUID
- Jarvis no triangula todo — los teammates hablan directamente entre ellos

## Escalación

Escalar a Thomas cuando:
- Equipo bloqueado tras 2 rondas de debate P2P sin resolución
- qc rechaza el mismo error 3 ciclos consecutivos
- La decisión requiere Thomas o Jeff (presupuesto, fecha, opinión, propuesta nueva)

Pasos:
```
1. SendMessage shutdown_request a todos los teammates activos
2. Esperar confirmaciones de shutdown
3. TeamCleanup
4. Reportar a Thomas en español: qué se hacía, cuál es el bloqueo, qué decisión se necesita
```
