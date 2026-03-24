# user_preferences.md — Perfil del Director
**Propietario:** Jarvis | **Actualizado:** 2026-03-24 | **Version:** 1.0
**Fuente:** Observacion directa de sesiones — primer dump completo

---

## Identidad

| Campo | Valor |
|-------|-------|
| Nombre | Thomas Reyes |
| Rol | Operations Lead, Keystone KSG |
| Universidad | EAFIT, Medellin — Ingenieria de Sistemas (activo) |
| Socio principal | Jeff Bania (Owner/Principal) |
| Ciudad | Medellin, Antioquia, Colombia |
| Email | thomasreyesr@gmail.com |
| Idioma con Jarvis | Espanol (siempre) |

---

## Estilo de Comunicacion

**Lo que Thomas quiere:**
- Directo, sin relleno, sin introduccion innecesaria
- Sin resumir lo que el acaba de decir ("como me indicaste..." — prohibido)
- Respuestas cortas cuando la tarea lo permite — una linea si es posible
- Que Jarvis de su opinion real si hay algo mejor o hay riesgos, ANTES de ejecutar
- Thomas prefiere discutir a que solo le den la razon

**Lo que Thomas NO quiere:**
- Emojis (nunca, a menos que el los pida)
- Summaries al final de cada respuesta ("en resumen, hice X...")
- Confirmaciones de lo obvio ("entendido, procedo a...")
- Verbosidad tecnica sin valor agregado

---

## Estilo Tecnico

**Preferencias de ejecucion:**
- Commit + push automatico al terminar cada tarea relevante — Thomas no quiere tener que pedirlo
- Un agente por sesion cuando se crean agentes nuevos — "vamos de 1 en 1"
- Los role.md siguen el estandar de 5 secciones exactas (Identity, Navigation, Autonomy, QC/Handoff, Evolution Zone)
- Evolution Zone: LOCKED en todos los agentes — solo ai_engineer via Amendment Pipeline puede proponer cambios
- Memory/ gitignored — Thomas lo sabe y lo acepta, backlog.md es local
- CLAUDE.md nunca supera 200 lineas — si crece, mover a protocols/ y dejar puntero

**Preferencias de arquitectura:**
- Minimalismo — no crear archivos que no se van a usar
- Agentes como especialistas puros con dominio acotado, no generalistas
- QC es obligatorio antes de entregar CUALQUIER output a Thomas o Jeff
- Los emails a Jeff son SIEMPRE bilingues: ingles primero, espanol debajo, separados por ---

---

## Contexto del Proyecto

**Keystone KSG:**
- Empresa de servicios de construccion/gestion con Jeff Bania como owner
- Thomas es Operations Lead — intermediario entre Jeff y los procesos operativos
- Contabilidad dual: COP para operaciones Colombia + USD para reportes Jeff/IRS
- Moneda default: COP (si Thomas dice un numero sin divisa, es pesos)
- Finca Barbosa: propiedad en construccion — proyecto Deck 12×50ft en ejecucion

**Jeff Bania / Kaiser:**
- Jeff usa el alias "Keyser Soze" (jeff.t.bania@gmail.com) para comunicacion digital
- Al escribirle a jeff.t.bania → dirigirse como "Keyser" o "Keyser Soze", NUNCA "Jeff"
- Siempre incluir los 3 emails de Jeff: To: jeffbania@gmail.com / CC: jeff.t.bania@gmail.com, jeff.t1.bania@gmail.com
- Kaiser revisa emails cada hora (Task Scheduler)
- Si Kaiser hace una pregunta que Thomas debe responder → email de espera a Kaiser + notificar Thomas

---

## Umbrales de Escalacion

| Jarvis maneja solo | Escalar a Thomas |
|--------------------|-----------------|
| Busqueda de informacion | Decisiones comerciales |
| Redaccion, formateo, logging | Aprobacion de gastos |
| Tareas operativas rutinarias | Compromisos de fecha/reunion |
| Respuestas a preguntas de Kaiser con datos conocidos | Opiniones personales de Thomas |
| | Propuestas nuevas fuera de proyectos activos |

---

## Perfil Academico (EAFIT)

- Carrera: Ingenieria de Sistemas — activo
- Meta academica: excelencia + portafolio tecnico diferenciador para CV senior
- Brecha: formalizar conocimiento practico en lenguaje teorico riguroso
- Fortalezas tecnicas: arquitectura de agentes IA, Python, FastAPI, seguridad, sistemas distribuidos
- Agente asignado: `academic_researcher` — Knowledge Bridge Keystone x EAFIT
- Formato de citas preferido: APA 7ma ed. / IEEE segun lo especifique el profesor
- Regla de oro: 3 fuentes academicas primarias obligatorias por entrega

---

## Datos Sensibles (uso operativo exclusivo)

- Direccion: Calle 38 #35a-06, Barrio El Salvador, Medellin
- Codigo postal: 050016
- Compartir solo si Keyser o Jeff lo solicitan explicitamente

---

## Patrones Observados

1. **Thomas piensa en secuencias** — cuando da un trabajo grande, luego pide hacerlo "de 1 en 1"
2. **Thomas revisa GitHub activamente** — detecta problemas de rendering (Mermaid, tablas) rapido
3. **Thomas valora la anticipacion** — Jarvis debe alertar riesgos antes de que Thomas los encuentre
4. **Thomas trabaja con contexto largo** — sesiones de construction intensiva, espera continuidad entre sesiones
5. **Thomas espera que Jarvis recuerde** — no quiere repetir contexto que ya dio anteriormente
6. **Thomas prefiere una decision clara** — si hay opciones, dar una recomendacion, no una lista infinita

---

*Actualizar cada vez que se observe un patron nuevo o una preferencia explicita de Thomas.*
*Propietario de escritura: Jarvis. Thomas puede corregir directamente.*
