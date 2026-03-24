# Protocolo — Traspaso de Sesión (Context Handoff)
**Activa este protocolo cuando el contexto esté al límite o Thomas lo ordene.**

<!-- CORE SECTION — READ ONLY -->

## Trigger

Activar inmediatamente cuando:
- Thomas diga: `"Jarvis, protocolo de traspaso"`
- Jarvis detecte que la ventana de contexto supera el **80%** de capacidad
- Las respuestas empiecen a perder coherencia con el inicio de la sesión (señal de context rot)

No pedir confirmación. Ejecutar directamente.

---

## Acción 1 — Guardar Estado

Analizar el estado actual de la sesión y sobrescribir `memory/estado_sesion.md` con esta estructura:

```markdown
# Estado de Sesión — [YYYY-MM-DD HH:MM COT]

## Objetivo Final de la Sesión
[Qué se estaba construyendo o resolviendo]

## Progreso Actual
- [x] Tarea completada 1
- [x] Tarea completada 2
- [ ] Tarea en curso (detenida aquí)
- [ ] Tarea pendiente siguiente

## Variables Críticas en Memoria
| Variable | Valor |
|----------|-------|
| Rama git activa | [nombre] |
| Último archivo editado | [ruta] |
| Último commit | [hash — mensaje] |
| Agentes convocados en esta sesión | [lista] |
| Decisiones tomadas por Thomas | [lista] |

## Bugs / Blockers Pendientes
- [descripción + archivo + línea si aplica]

## Contexto Técnico a Preservar
[Decisiones de arquitectura, razones de diseño, advertencias activas]

## Siguiente Paso Exacto
[Instrucción precisa de qué ejecutar al reanudar — suficientemente detallada para que una sesión nueva la retome sin ambigüedad]
```

---

## Acción 2 — Instrucción al Usuario

Una vez guardado `memory/estado_sesion.md`, detener cualquier otra ejecución y responder **exactamente**:

---

⚠️ **Contexto guardado.** Thomas, por favor ejecuta `/clear` en tu terminal para limpiar la memoria. Luego, envíame este mensaje para continuar: *Jarvis, lee memory/estado_sesion.md y ejecuta el siguiente paso.*

---

## Al Reanudar (nueva sesión)

Cuando Thomas envíe `"Jarvis, lee memory/estado_sesion.md y ejecuta el siguiente paso"`:

1. Leer `memory/estado_sesion.md` completo
2. Leer `memory/keystone_kb.md` para recargar contexto de negocio
3. Confirmar a Thomas en 2 líneas: qué se hizo, cuál es el siguiente paso
4. Ejecutar el siguiente paso sin pedir más contexto

<!-- END OF CORE SECTION -->
