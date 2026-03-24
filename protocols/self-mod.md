# Protocolo — Auto-Modificación y Aprendizaje Continuo
**Lee este archivo cuando detectes un error recurrente, corrección de Thomas, o patrón nuevo.**

## Evolution Zone — Opt-In (DESACTIVADA por defecto)

**Regla estricta:** Jarvis y todos los sub-agentes tienen PROHIBIDO editar el `role.md`, las herramientas (`tools/`) o cualquier sección de Evolution Zone de cualquier agente — a menos que Thomas dé la orden explícita:
- `"Jarvis, activa la evolución para el agente [nombre]"`
- `"Jarvis, entrena a [agente] para [directriz]"`
- `"Actualiza la Evolution Zone de [agente]"`

**Si un agente detecta una mejora posible:** registrar la sugerencia en `memory/keystone_kb.md` bajo `## Pending Suggestions` — NO editar ningún archivo de agente. Thomas revisará las sugerencias y decidirá cuáles activar.

**Excepción única:** `memory/keystone_kb.md` (sección Learned Patterns) — Jarvis puede añadir entradas después de cada team run sin autorización explícita. No aplica a `role.md` ni `tools/`.

---

## Autorización de Modificación

| Target | Acción | Condición |
|--------|--------|-----------|
| `memory/keystone_kb.md` | Añadir / actualizar entradas | Root cause confirmado |
| `EVOLUTION ZONE` de `CLAUDE.md` | Añadir reglas operativas | Patrón observado ≥2 veces |
| `EVOLUTION ZONE` de cualquier `.claude/agents/*.md` | Añadir comportamientos mejorados | Root cause confirmado |
| Scripts en `tools/*.py` | Editar para bugs o cambios de formato | Comentario changelog obligatorio |

**Prohibido:** Nunca modificar la sección CORE de ningún archivo.

## Formato Changelog (obligatorio en toda auto-modificación)

```
<!-- [YYYY-MM-DD] Changed: [qué] — Reason: [por qué] — Triggered by: [error/corrección Thomas/patrón] -->
```

## Self-Resolution Loop

```
Error / corrección / patrón detectado
        ↓
Identificar root cause
        ├── Regla de negocio o cambio de formato
        │       → Actualizar memory/keystone_kb.md
        │
        ├── Mejora de comportamiento de un agente
        │       → Editar EVOLUTION ZONE del agente correspondiente
        │
        └── Bug en script de tools/
                → Corregir el script con comentario changelog
        ↓
Aplicar el cambio
        ↓
En el siguiente team run → verificar que el fix resolvió el problema
        ↓
Si no resolvió → escalar a Thomas (ver protocols/equipos.md)
```

## Training Orders (Entrenamiento de Agentes)

Cuando Thomas emita una orden del tipo "entrena a [agente] para X", "ajusta [agente]", o "mejora [agente]":

```
1. Leer agentes/[nombre]/role.md completo
        ↓
2. Identificar el target de la modificación:
   ├── Nueva habilidad / tono / restricción → inyectar en EVOLUTION ZONE
   └── Cambio de identidad o reglas base   → escalar a Thomas (no tocar CORE)
        ↓
3. Editar EVOLUTION ZONE del agente con la directriz nueva
   Formato obligatorio:
   <!-- [YYYY-MM-DD] Training: [directriz añadida] — Ordered by: Thomas -->
   [directriz en texto plano, máx. 3 líneas]
        ↓
4. Registrar en memory/keystone_kb.md bajo ## Team Evolution
   Formato:
   ## [YYYY-MM-DD] TEAM EVOLUTION: [agente] — [título corto]
   Directriz: [descripción]
   Fuente: Training Order de Thomas
        ↓
5. Confirmar a Thomas: agente reentrenado, archivo actualizado, KB registrado
```

**Límites del entrenamiento:**
- Solo se modifica la `EVOLUTION ZONE` — la sección `CORE` de cualquier agente es intocable
- Si la orden implica un cambio de herramientas (`tools:`) o modelo (`model:`), confirmar con Thomas antes de editar el frontmatter
- Máximo una Training Order por sesión por agente — si hay conflicto entre directrices, escalar

---

## Actualización del Knowledge Base

Después de cada team run completado, Jarvis evalúa:

1. ¿Hubo una corrección de Thomas que revela una regla de negocio desconocida?
   → Añadir en `memory/keystone_kb.md` bajo `## Learned Patterns`

2. ¿Hubo un formato nuevo aprobado (factura, reporte, contrato)?
   → Documentar el formato en `memory/keystone_kb.md`

3. ¿Hubo un error recurrente del mismo agente?
   → Añadir regla en su `EVOLUTION ZONE`

Formato de entrada en KB:
```markdown
## [YYYY-MM-DD] [categoría]: [título corto]
[descripción de la lección, máx. 3 líneas]
Fuente: [corrección Thomas / error detectado / patrón observado]
```
