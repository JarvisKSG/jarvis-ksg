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
| `n8n_engineer` | `agentes/n8n_engineer/` | Automatización n8n — diseña y construye workflows, integra APIs REST, maneja webhooks, transforma JSON y sincroniza datos entre sistemas. |
| `slack_expert` | `agentes/slack_expert/` | Integración Slack — desarrolla bots, Block Kit UIs, slash commands, event handlers y OAuth flows para el workspace Keystone. Todo mensaje pasa por `qc` antes de enviarse. |
| `git_expert` | `agentes/git_expert/` | Control de versiones y custodio de repos — branching, commits convencionales, resolución de conflictos, rebase, releases/tags y auditoría permanente del .gitignore. Operaciones destructivas requieren QC. |
| `python_developer` | `agentes/python_developer/` | Backend Python y procesamiento de datos — scripts de automatización, OCR, extracción de datos, Pandas/JSON, integraciones API. Todo script requiere QC antes de entregarse. |
| `database_architect` | `agentes/database_architect/` | Arquitectura de datos — modelado relacional (3FN), optimización de queries, schemas para PostgreSQL/Airtable/Google Sheets, DDL con migraciones. Todo DDL requiere QC. |
| `tech_writer` | `agentes/tech_writer/` | Documentación y gestión del conocimiento — guías de agentes, diagramas Mermaid, changelogs, onboarding. Lee todos los role.md y protocols/ para mantener docs sincronizados. |
| `frontend_engineer` | `agentes/frontend_engineer/` | Arquitectura de interfaces y UX — React 18+/Next.js 14+, Tailwind CSS (obligatorio), dashboards Caja Negra, UI de procesamiento OCR de recibos, consumo de APIs. Todo componente requiere QC antes de deployar. |
| `ai_engineer` | `agentes/ai_engineer/` | Arquitecto de inteligencia y optimizador LLM — auditorías semanales de prompts, control de costos y tokens, arquitectura RAG, selección de modelos, y Amendment Pipeline para evolución del enjambre. **Único agente autorizado a proponer cambios en role.md de otros agentes** (siempre vía QC + aprobación Thomas). Evolution Zone abierta (Opt-In). |
| `scrum_master` | `agentes/scrum_master/` | Director de Proyectos y Gestor de Producto — mantiene `memory/backlog.md` como fuente de verdad, prioriza por Impacto/Dificultad, planifica sprints semanales, registra ideas de Thomas, trackea hallazgos de auditoría y hitos de despliegue. |
| `entity_intelligence` | `agentes/entity_intelligence/` | Director de Contexto Relacional y Diplomacia de IA — mantiene `memory/social_graph.md` con perfiles de entidades humanas (Thomas, Jeff, clientes) y agentes externos (Keyser Soze). Escáner pasivo de preferencias y relaciones. Único agente autorizado a escribir en social_graph.md. |
| `researcher_agent` | `agentes/researcher_agent/` | Analista de Innovación y Vigilancia Tecnológica — evalúa alternativas tecnológicas, benchmarks de OCR, APIs de bajo costo, y tendencias IA. Produce Reportes de Innovación con formato [Tecnología | Beneficio | Dificultad]. Routing P2P a python_developer, ai_engineer, database_architect. |
| `data_scientist` | `agentes/data_scientist/` | Estratega de Datos e Insights de Negocio — transforma los 25 campos de Caja Negra en KPIs estratégicos, detecta anomalías de precio por proveedor, genera proyecciones de cierre de mes y Reportes de Salud Financiera. P2P con database_architect (vistas SQL) y frontend_engineer (specs de dashboard). |
| `security_auditor` | `agentes/security_auditor/` | Guardián de Integridad y Privacidad — audita superficie de ataque del enjambre (OWASP, prompt injection, secrets, OAuth tokens, .gitignore). Solo lee, nunca modifica. Routing P2P a python_developer, git_expert, n8n_engineer, email_manager. Hallazgos CRÍTICOS escalan directo a Thomas. |
| `tester_automation` | `agentes/tester_automation/` | Jefe de Calidad y Robustez — escribe Pytest (Python) y Jest/Vitest (React) tests, crea mocks de recibos con errores típicos, audita cobertura. Regla: código sin test file es falla C2. Tests en tests/. P2P con python_developer, frontend_engineer, data_scientist. |
| `ux_designer` | `agentes/ux_designer/` | Arquitecto de Experiencia y Flujos de Trabajo — diseña wireframes (texto estructurado), arquitectura de información y handoff specs antes de que frontend_engineer toque código. Progressive disclosure: Nivel 1 (4 KPIs), Nivel 2 (tabs), Nivel 3 (drill-down). Regla de 5 segundos para Jeff. |
| `api_backend` | `agentes/api_backend/` | Arquitecto de Servicios y Conectividad — diseña e implementa la capa FastAPI entre motor OCR Python y dashboard React. OpenAPI 3.1, Bearer Token JWT, contratos JSON para los 17 KPIs, manejo de errores sin stack traces expuestos. |
| `compliance` | `agentes/compliance/` | Especialista Normativa Fiscal DIAN/IRS — valida CUFE, NIT, IVA en facturas colombianas y mapea categorías de gasto a IRS Schedule C para deducibilidad de Jeff Bania. Regla de oro DIAN: sin CUFE no hay factura válida. |
| `demo_expert` | `agentes/demo_expert/` | Maestro de Narrativa y Product Showcase — traduce capacidades técnicas del enjambre a valor de negocio comprensible para Jeff. Walkthroughs, ROI narratives, pitch emails bilingües. Regla del Número Único: un impacto por comunicación. |

| `estimation_specialist` | `agentes/estimation_specialist/` | Analista Senior de Costos y Predictor de Presupuestos — genera matrices de costos unitarios desde Caja Negra, modelos de regresion de precios, y presupuestos con margen de error para licitaciones. Colabora con data_scientist y researcher_agent. |

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
