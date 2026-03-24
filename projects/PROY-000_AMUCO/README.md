# AMUCO INC. — AI Agent System
**PROY-005 | Agente de Inteligencia Artificial para Atención al Cliente**

Sistema de IA compuesto por dos agentes independientes que automatizan la atención técnica y comercial de AMUCO INC., línea Coatings & Paints.

---

## Componentes del sistema

```
PROY-005_Agente_IA_AMUCO/
├── rag_chatbot.py          → Agente 1: Chatbot técnico (web + WhatsApp)
├── amuco_reminder_agent.py → Agente 2: Recordatorios de cotizaciones
├── rag_indexer.py          → Indexador de fichas técnicas (ejecutar 1 vez)
├── build_catalog.py        → Generador de catálogo (ejecutar 1 vez)
├── product_catalog.json    → Catálogo de 27 productos
├── chroma_db/              → Base vectorial con 709 chunks indexados
└── fichas_tecnicas/        → 412 archivos PDF/DOCX de 33 productos
```

---

## Agente 1 — Chatbot RAG de Consultas Técnicas

### Qué hace
Responde consultas técnicas y comerciales sobre los productos de la línea Coatings & Paints de AMUCO, actuando como un asesor técnico de ventas. Disponible vía web y WhatsApp.

### Cómo funciona

```
Cliente hace una pregunta
        ↓
PASO 1 — Clasificación local (sin API)
  ¿La pregunta menciona un producto o término técnico?
  → SÍ → camino ESPECÍFICO
  → NO → camino GENERAL
        ↓
PASO 2A — GENERAL (pregunta exploratoria)
  El modelo tiene el catálogo de 27 productos en su contexto
  Responde de forma conversacional, pide más contexto si es necesario

PASO 2B — ESPECÍFICO (producto o propiedad mencionada)
  1. Convierte la pregunta en vector numérico (embedding)
  2. Busca en ChromaDB los chunks más relevantes
  3. Carga el PDF completo del producto encontrado
  4. El modelo lee la ficha técnica y responde con datos reales
        ↓
PASO 3 — Entrega
  Limpia la respuesta y la devuelve al cliente
```

### Stack técnico
- **Python 3.12**
- **Flask** — servidor web en puerto 5001
- **ChromaDB** — base vectorial local (709 chunks, 33 productos)
- **Gemini API** — embeddings (`gemini-embedding-001`) + generación (`gemini-2.5-flash`)
- **Twilio** — integración WhatsApp
- **ngrok** — exponer localhost al exterior para pruebas

### Cómo arrancar
```bash
# Verificar que no hay procesos en el puerto
netstat -ano | grep 5001
# Matar por PID si hay algo: taskkill /F /PID [PID]

# Arrancar el servidor
cd PROY-005_Agente_IA_AMUCO
/c/Python312/python.exe rag_chatbot.py

# En otra terminal, exponer al exterior (para WhatsApp)
ngrok http 5001
```

### Endpoints disponibles
| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Interfaz web del chatbot |
| `POST /ask` | API JSON para consultas |
| `POST /whatsapp` | Webhook para Twilio WhatsApp |

### Configuración WhatsApp (Twilio Sandbox)
- Número: +1 415 523 8886
- Activar con: `join determine-begun`
- Webhook: `https://[ngrok-url]/whatsapp` → configurar en Twilio → Sandbox settings

---

## Agente 2 — Recordatorios Automáticos de Cotizaciones

### Qué hace
Detecta cotizaciones en estado `quoted` con 2+ días sin respuesta del cliente y envía un email de seguimiento personalizado en el idioma del cliente (ES/EN/PT), con el tono real del asesor comercial.

### Cómo funciona

```
Ejecución diaria (manual o programada)
        ↓
1. LOGIN a kiwi.amucoinc.com (sesión + CSRF automáticos)
        ↓
2. CONSULTA cotizaciones del agente comercial
   → Filtra: status "quoted" + 2+ días sin respuesta
   → Resultado: lista de clientes que no han respondido
        ↓
3. POR CADA COTIZACIÓN:
   → Obtiene detalle: producto, cantidad, precio, ETD, incoterm
   → Obtiene emails del cliente desde el perfil
   → Detecta idioma (ES/EN/PT) por nombre de empresa
   → Genera email personalizado con datos reales de la cotización
        ↓
4. ENVÍA el recordatorio
   → TEST_MODE=True: va a email de prueba (no al cliente real)
   → TEST_MODE=False: va al cliente real (requiere aprobación)
        ↓
5. LOG del resultado
```

### Acceso a kiwi.amucoinc.com (sin API oficial)
El sistema de AMUCO no tiene API pública. Los endpoints internos del DataTable fueron mapeados desde el browser (DevTools → Network) y el script los consume autenticándose igual que un usuario normal:

| Dato | Endpoint interno |
|------|-----------------|
| Lista de cotizaciones | `/administrator/amuco_customer_request/get_data_table_quotation` |
| Detalle de oferta | `/administrator/amuco_offers_sent_customers/get_data_by_id?id={id}` |
| Emails del cliente | `/administrator/amuco_customers/view/{customer_id}?popup=show` |

### Tono de los emails
Templates entrenados con correos reales del asesor comercial. Características:
- Saludo personalizado con nombre del cliente
- Referencia al producto y monto específico de la cotización
- Mención de condiciones de mercado como contexto de urgencia
- Oferta de ayuda para facilitar la decisión
- Cierre directo: "Quedo muy atento a su respuesta"
- Firma bilingüe: "Saludos cordiales / Best Regards"

### Cómo ejecutar
```bash
# Modo simulación (sin envíos reales)
/c/Python312/python.exe amuco_reminder_agent.py

# Modo envío real (requiere aprobación)
/c/Python312/python.exe amuco_reminder_agent.py --send
```

### Modos de operación
| Variable | Valor | Comportamiento |
|----------|-------|----------------|
| `DRY_RUN=True` | Simulación | No envía nada, solo muestra qué enviaría |
| `TEST_MODE=True` | Prueba | Envía a email de prueba, no al cliente real |
| `TEST_MODE=False` | Producción | Envía a clientes reales — requiere aprobación |

---

## Integración con Jarvis (Orquestador)

Ambos agentes forman parte del ecosistema Keystone de Jarvis:

- **Notificaciones** → cuando el agente de recordatorios envía un email, puede notificar al asesor comercial vía Slack
- **Coordinación** → Jarvis puede disparar el agente de recordatorios de forma programada
- **Logs** → los resultados se registran para seguimiento

---

## Estado actual

| Componente | Estado |
|-----------|--------|
| Chatbot web (localhost:5001) | Funcionando |
| Chatbot WhatsApp (Twilio sandbox) | Funcionando |
| Agente de recordatorios (TEST_MODE) | Funcionando |
| Indexación de fichas técnicas | 709 chunks, 33 productos |
| Producción WhatsApp (número propio) | Pendiente — requiere aprobación Meta |
| Agente de recordatorios (producción) | Pendiente — requiere aprobación AMUCO |

---

## Archivos sensibles (NO en git)
- `brief.md` — credenciales y datos del proyecto
- Variables de entorno con API keys y contraseñas
