# Agent Registry — Directorio de Agentes Keystone
**Lee este archivo antes de invocar un equipo o fabricar un agente nuevo.**

Jarvis debe consultar este índice primero. Si el dominio necesario no está cubierto, ejecutar el Agent Factory (`protocols/equipos.md` — Paso 0) antes de proceder.

---

## Agentes Activos

| Nombre | Workspace | Descripción |
|--------|-----------|-------------|
| `qc` | `agentes/qc/` | Control de Calidad — valida C1–C7 todo output antes de llegar a Thomas o Jeff. Invocar siempre al final de cualquier equipo. |
| `contador` | `agentes/contador/` | Contabilidad y procesamiento financiero — extrae campos de recibos/facturas, genera reportes estructurados, registra en Caja Negra. |
| `email_manager` | `agentes/email_manager/` | Gestión de correos Gmail — único agente autorizado para leer bandeja, redactar y enviar correos. Todo borrador pasa por `qc` antes de envío. |

---

## Agentes Planificados (por crear)

| Nombre | Dominio | Estado |
|--------|---------|--------|
| `inventario` | Inventario Finca Barbosa | Pendiente |
| `rrhh` | Evaluación CVs, framework Keyser v4 | Pendiente |
| `investigador` | Research autónomo (web, papers) | Pendiente |
| `seguridad` | Validación contenido externo, anti-inyección | Pendiente |
| `whatsapp` | Daemon WhatsApp +57 310 338 4459 | Pendiente |

---

## Cómo Añadir un Agente

Cuando el Agent Factory fabrique un agente nuevo, Jarvis añade una fila en la tabla "Activos" con:
- Nombre exacto (minúsculas, sin espacios)
- Ruta del workspace
- Descripción de una línea (use-case oriented)
