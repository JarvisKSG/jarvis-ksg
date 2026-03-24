# ACAD-001 — Knowledge Bridge: Keystone KSG × EAFIT Ingeniería de Sistemas
**Agente:** `academic_researcher`
**Fecha:** 2026-03-24
**Proposito:** Conectar cada tecnologia en produccion de Keystone con su fundamento teorico academico en el curriculo de Ingenieria de Sistemas EAFIT — para que Thomas pueda formalizar experiencia practica como conocimiento academico riguroso.

---

> **Uso de este documento:** Antes de cualquier entrega en EAFIT, Thomas consulta este bridge para identificar los conceptos teoricos que ya domina en la practica y los papers que los respaldan. Actualizar cada vez que Keystone adopte una nueva tecnologia o Thomas inicie una nueva materia.

---

## Mapa de Conexiones — Keystone × Materias EAFIT

### 1. Arquitectura de Agentes IA / Sistema Multi-Agente → Inteligencia Artificial

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| Enjambre de 28 agentes especializados con roles definidos | Sistemas Multi-Agente (MAS) — Wooldridge & Jennings | AVANZADO — implemento en produccion |
| `qc` como agente validador con 7 capas C1-C7 | Agentes deliberativos con BDI (Belief-Desire-Intention) | MEDIO — aplica sin conocer el modelo formal |
| `ai_engineer` con Amendment Pipeline | Meta-razonamiento y auto-modificacion de agentes | AVANZADO — diseño el protocolo |
| `scrum_master` orquestando sprints | Coordinacion y planificacion en MAS | AVANZADO |
| `reinforcement_learning_engineer` (en reserva) | Q-Learning, Policy Gradient, Model-Based RL | BASICO — conoce el concepto, no lo ha implementado |

**Papers recomendados (fuentes primarias PRIMARIA):**
1. Wooldridge, M., & Jennings, N.R. (1995). *Intelligent agents: Theory and practice*. The Knowledge Engineering Review, 10(2), 115–152. DOI: 10.1017/S0269888900008122
2. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Prentice Hall. [Capitulos 2, 17, 21]
3. Sutton, R.S., & Barto, A.G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. [Capitulos 1-3 para fundamentos RL]

**Reformulacion para CV de Thomas:**
> "Diseño e implementacion de un sistema multi-agente distribuido (MAS) de 28 agentes especializados bajo principios de coordinacion deliberativa y division de trabajo por dominio, aplicado a la automatizacion de procesos contables y de gestion de proyectos."

---

### 2. FastAPI + REST + OpenAPI → Arquitectura de Software / Redes

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| FastAPI con Bearer Token JWT, OpenAPI 3.1 | Arquitectura REST (Fielding, 2000) — Constraints: stateless, uniform interface | AVANZADO |
| `api_backend` con 6 endpoints definidos | API Design — Richardson Maturity Model (Nivel 3: HATEOAS) | MEDIO |
| Service Workers interceptando llamadas HTTP | Proxy Pattern / Cache-Control en redes | MEDIO |
| Bearer Token + OAuth para Google Drive | Autenticacion federada, OAuth 2.0 RFC 6749 | AVANZADO |

**Papers recomendados:**
1. Fielding, R.T. (2000). *Architectural Styles and the Design of Network-based Software Architectures*. Doctoral dissertation, UC Irvine. [Capitulo 5 — REST]
2. Richardson, L., Amundsen, M., & Ruby, S. (2013). *RESTful Web APIs*. O'Reilly Media.
3. Hardt, D. (Ed.). (2012). *The OAuth 2.0 Authorization Framework*. RFC 6749. IETF. https://datatracker.ietf.org/doc/html/rfc6749

**Reformulacion para CV:**
> "Implementacion de API RESTful nivel 3 (Richardson Maturity Model) con autenticacion OAuth 2.0 y JWT, siguiendo estandares OpenAPI 3.1 — aplicada como capa de integracion entre motor OCR Python y dashboard React."

---

### 3. OCR Pipeline + Python Async → Algoritmos / Estructuras de Datos / Sistemas Operativos

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| `parse_recibo()` con 5 jerarquias de excepcion | Programacion defensiva, manejo estructurado de errores | AVANZADO |
| OCR async con `run_in_executor` | Concurrencia vs paralelismo, event loop, thread pool | MEDIO |
| 29 tests pytest con 95% coverage | Pruebas unitarias, cobertura de codigo, TDD | AVANZADO |
| Pipeline: imagen → OCR → parse → validar → guardar | Patron de diseño Pipeline / Chain of Responsibility | AVANZADO |
| PaddleOCR vs Tesseract benchmarking | Analisis comparativo de algoritmos, complejidad temporal | MEDIO |

**Papers recomendados:**
1. Python Software Foundation. (2023). *asyncio — Asynchronous I/O*. Python 3.12 Documentation. https://docs.python.org/3/library/asyncio.html [SECUNDARIA — doc oficial]
2. Beck, K. (2002). *Test Driven Development: By Example*. Addison-Wesley Professional.
3. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley. [Patron Chain of Responsibility, pp. 223-232]

---

### 4. AES-256-GCM + Security Auditing → Seguridad Informatica

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| `db_backup.py` con AES-256-GCM, nonce aleatorio | Criptografia simetrica, modos de operacion (GCM = CTR + GHASH) | MEDIO |
| SHA-256 checksum en cada backup | Funciones hash criptograficas, integridad de datos | AVANZADO |
| Anti-Injection Gate en `email_manager` | OWASP Top 10, prompt injection como vector de ataque nuevo | AVANZADO |
| `.gitignore` auditado para secretos | Gestion de secretos, principio de minimo privilegio | AVANZADO |
| Plan de desastre — recuperacion < 15 min | RTO/RPO, Business Continuity Planning (BCP) | MEDIO |

**Papers recomendados:**
1. NIST. (2001). *Advanced Encryption Standard (AES)*. FIPS PUB 197. https://doi.org/10.6028/NIST.FIPS.197
2. Dworkin, M. (2007). *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*. NIST SP 800-38D.
3. OWASP Foundation. (2021). *OWASP Top Ten 2021*. https://owasp.org/www-project-top-ten/

**Reformulacion para CV:**
> "Implementacion de sistema de backup cifrado end-to-end con AES-256-GCM (NIST FIPS 197), verificacion de integridad SHA-256, y plan de continuidad de negocio con RTO < 15 minutos — aplicado a datos financieros con requisitos de confidencialidad."

---

### 5. Google Sheets como Base de Datos / PostgreSQL → Bases de Datos

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| 25 columnas estructuradas en Sheets con esquema definido | Modelo relacional, normalizacion (1FN, 2FN, 3FN) | MEDIO |
| DASHBOARD_ANUAL con formulas SUMIF/QUERY | Vistas SQL, agregaciones, GROUP BY | MEDIO |
| Cache en memoria para KPIs (TTL 5 min) | Gestion de cache, estrategias de invalidacion | AVANZADO |
| Indice de facturas con ID Unico | Indices de base de datos, B-tree, clave primaria | BASICO — usa el concepto sin saber el subyacente |
| Migracion planificada Sheets → PostgreSQL | Estrategias de migracion de datos, DDL, DML | BASICO |

**Papers recomendados:**
1. Codd, E.F. (1970). *A relational model of data for large shared data banks*. Communications of the ACM, 13(6), 377–387. DOI: 10.1145/362384.362685
2. Date, C.J. (2003). *An Introduction to Database Systems* (8th ed.). Addison-Wesley. [Capitulos 6-9 — Normalizacion]
3. PostgreSQL Global Development Group. (2024). *PostgreSQL 16 Documentation*. https://www.postgresql.org/docs/16/ [SECUNDARIA]

---

### 6. Progressive Web App / React → Desarrollo Web / Computacion Movil

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| Service Workers con Stale-While-Revalidate | Cache API, estrategias de cache (Cache-First, Network-First) | AVANZADO |
| manifest.json + display: standalone | Progressive Enhancement, offline-first design | AVANZADO |
| Lighthouse 100/100 PWA audit | Web performance metrics (LCP, FID, CLS — Core Web Vitals) | MEDIO |
| React 18+ con componentes funcionales y hooks | Programacion reactiva, inmutabilidad, patron Observer | MEDIO |
| responsive design mobile-first | Diseño adaptativo, breakpoints, accesibilidad WCAG | MEDIO |

**Papers recomendados:**
1. Google. (2021). *Web Vitals*. https://web.dev/vitals/ [SECUNDARIA — referencia tecnica oficial]
2. Grigorik, I. (2013). *High Performance Browser Networking*. O'Reilly. Capitulo 11: Building for Mobile.
3. Osmani, A. (2017). *The App Shell Model*. Google Developers. [SECUNDARIA — referencia arquitectura PWA]

---

### 7. Sistema Distribuido de Agentes → Sistemas Distribuidos

| Keystone (practica real) | Concepto EAFIT (teoria) | Nivel de dominio de Thomas |
|--------------------------|------------------------|---------------------------|
| 28 agentes ejecutando en paralelo con comunicacion P2P | Sistemas distribuidos, coordinacion, consistencia eventual | AVANZADO |
| QC como punto de validacion central | Arquitecturas centralizadas vs descentralizadas, punto de fallo unico | AVANZADO |
| handoff.md para transferencia de contexto entre sesiones | Protocolos de comunicacion, paso de mensajes | AVANZADO |
| Amendment Pipeline con 6 pasos de aprobacion | Protocolos de consenso (no blockchain, pero analogo) | MEDIO |

**Papers recomendados:**
1. Lamport, L. (1978). *Time, Clocks, and the Ordering of Events in a Distributed System*. Communications of the ACM, 21(7), 558–565. [Clasico fundamental]
2. Tanenbaum, A.S., & Van Steen, M. (2016). *Distributed Systems: Principles and Paradigms* (3rd ed.). Prentice Hall.
3. Brewer, E. (2012). *CAP twelve years later: How the 'rules' have changed*. Computer, 45(2), 23–29. DOI: 10.1109/MC.2012.37

---

## Proximas Conexiones por Desarrollar

| Tecnologia Keystone | Materia EAFIT probable | Estado |
|--------------------|----------------------|--------|
| n8n workflows (automatizacion visual) | Sistemas de Informacion / BPM | Pendiente mapeo |
| Compliance DIAN (normativa fiscal colombiana) | Derecho Informatico / Sistemas de Informacion Empresarial | Pendiente mapeo |
| TRM sync (datos.gov.co API) | Sistemas de Informacion Gubernamental / Open Data | Pendiente mapeo |
| Mermaid diagrams (documentacion arquitectura) | Modelado de Sistemas / UML | Pendiente mapeo |
| GitHub Actions / CI-CD (cuando se implemente) | DevOps / Ingenieria de Software | Pendiente — activar con Hito Cloud |

---

## Guia de Uso para Thomas

**Cuando tienes una entrega proxima:**
1. Dile a `academic_researcher` la materia, el tema y la fecha
2. El agente identifica las conexiones de este bridge y las amplifica
3. Recibe un borrador con estructura academica, citas, y lenguaje formal
4. `qc` valida antes de que lo entregues

**Para el CV senior:**
- Cada seccion de este bridge es un bullet point para tu CV o LinkedIn
- Usa las reformulaciones para convertir "hice un backup" en logros con impacto tecnico verificable y referencias academicas

---

*Generado por: `academic_researcher` | Fuentes ADN: VoltAgent scientific-literature-researcher + research-analyst | Pendiente: confirmar materias activas semestre 2026-1 con Thomas*
