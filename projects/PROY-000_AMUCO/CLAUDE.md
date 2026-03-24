# PROY-005 — Agente IA AMUCO | Contexto para IA

**Proyecto:** Sistema de atención e IA para AMUCO INC., línea Coatings & Paints
**Owner:** Thomas Reyes (Keystone) + Harold Santiago (AMUCO)
**Estado:** Desarrollo activo — versión estable inicial

---

## 1. QUÉ HACE ESTE PROYECTO (resumen de una línea por agente)

- **`chatbot/rag_chatbot.py`** → servidor Flask en puerto 5001. Responde consultas técnicas sobre 33 productos usando RAG (ChromaDB + Gemini). Disponible por web y WhatsApp.
- **`reminder_agent/amuco_reminder_agent.py`** → script standalone. Se conecta al CRM de AMUCO (`kiwi.amucoinc.com`), detecta cotizaciones sin respuesta en 2+ días y envía emails de seguimiento al cliente.

---

## 2. ARCHIVOS QUE NO ESTÁN EN EL REPO (crítico)

Estos archivos son necesarios para que el sistema funcione pero **no están en git** por seguridad o tamaño:

| Archivo / Carpeta | Por qué no está | Cómo conseguirlo |
|---|---|---|
| `brief.md` | Credenciales sensibles del proyecto | Pedirle a Thomas |
| `chatbot/fichas_tecnicas/` | 412 PDFs/DOCX propietarios de AMUCO (33 productos) | Descargar desde SharePoint AMUCO con `_utils/download_sharepoint.py` |
| `chatbot/chroma_db/` | Base vectorial generada (709 chunks) | Ejecutar `chatbot/build_catalog.py` luego `chatbot/rag_indexer.py` |
| `chatbot/product_catalog.json` | Catálogo generado automáticamente | Ejecutar `chatbot/build_catalog.py` |

**Si clonas el repo desde cero, el chatbot NO arranca hasta que regeneres chroma_db y product_catalog.json.**

---

## 3. CREDENCIALES — DÓNDE ESTÁN Y QUÉ NECESITAS

⚠️ **Las credenciales están hardcodeadas directamente en los scripts** (decisión de velocidad en desarrollo). En producción deberían moverse a variables de entorno.

### Chatbot (`chatbot/rag_chatbot.py`, línea 18)
```python
GEMINI_API_KEY = "..."   # Google AI Studio — proyecto AMUCO
```
- Consola: [aistudio.google.com](https://aistudio.google.com)
- Modelo usado: `gemini-2.5-flash` (generación) + `gemini-embedding-001` (embeddings)
- Si la key expira o cambia: actualizar en `rag_chatbot.py` L18 y en `rag_indexer.py`

### Agente de recordatorios (`reminder_agent/amuco_reminder_agent.py`, líneas 29-31)
```python
AMUCO_URL  = "https://kiwi.amucoinc.com"
AMUCO_USER = "harold.santiago@amucoinc.com"
AMUCO_PASS = "..."   # contraseña del CRM de Harold
```
- Si Harold cambia su contraseña: actualizar `AMUCO_PASS`

### Gmail API (envío de emails desde Jarvis)
- El agente usa `agents/2A-CONTADOR/jarvis_send_email.py` del repo principal Keystone
- Token OAuth: `agents/2A-CONTADOR/jarvis_token.json`
- Si hay error 403: el token expiró, correr el script de auth de Jarvis
- **Este script no está en este repo** — está en el repo Keystone

### Twilio (WhatsApp)
- Las credenciales de Twilio están en `brief.md` (no en git)
- Número sandbox: +1 415 523 8886
- Para activar el sandbox desde WhatsApp: enviar `join determine-begun`
- Webhook: `https://[ngrok-url]/whatsapp` — configurar en Twilio dashboard cada vez que ngrok cambia URL

---

## 4. CÓMO ARRANCAR DESDE CERO (después de clonar)

### Paso 1 — Dependencias
```bash
/c/Python312/python.exe -m pip install flask chromadb google-genai pdfplumber python-docx requests langdetect
```

### Paso 2 — Conseguir las fichas técnicas
```bash
# Con acceso al SharePoint de AMUCO (credenciales en brief.md):
/c/Python312/python.exe _utils/download_sharepoint.py
```
O copiar manualmente la carpeta `fichas_tecnicas/` al directorio `chatbot/`.

### Paso 3 — Construir el catálogo y la base vectorial
```bash
cd chatbot
/c/Python312/python.exe build_catalog.py    # genera product_catalog.json
/c/Python312/python.exe rag_indexer.py      # genera chroma_db/ (tarda ~5-10 min)
```

### Paso 4 — Arrancar el chatbot
```bash
# Verificar que el puerto 5001 está libre
netstat -ano | grep 5001
# Si hay procesos: taskkill /F /PID [numero]

/c/Python312/python.exe chatbot/rag_chatbot.py
# → Servidor en http://localhost:5001
```

### Paso 5 — WhatsApp (opcional, solo si necesitas probarlo)
```bash
# En terminal separada:
ngrok http 5001
# Copiar la URL https://xxxxx.ngrok-free.app
# Ir a Twilio → Sandbox Settings → pegar URL + /whatsapp
# Desde WhatsApp al +1 415 523 8886: "join determine-begun"
```

---

## 5. CÓMO FUNCIONA EL CHATBOT (arquitectura interna)

```
Cliente escribe pregunta
        ↓
_classify_query(query)  ←  clasificador local, SIN API, sin costo
  → "GENERAL" si no menciona producto específico
  → "SPECIFIC" si menciona nombre de producto o término técnico
        ↓
GENERAL → ask_gemini_general(query, history)
  El catálogo de 27 productos está baked in el SYSTEM_PROMPT (f-string)
  No hace búsqueda vectorial
        ↓
SPECIFIC → ask_gemini_specific(query, context_chunks, history)
  1. Convierte query en embedding (Gemini embedding-001)
  2. Busca TOP_K=6 chunks en ChromaDB
  3. Carga PDFs completos de los productos encontrados (MAX_FULL_DOCS=3)
  4. Pasa el texto completo como contexto inline al modelo
        ↓
_generate(contents, temperature)
  - Siempre usa system_instruction=SYSTEM_PROMPT
  - SYSTEM_PROMPT incluye el catálogo completo (f-string)
  - max_output_tokens=4096
  - _strip_signature() elimina firma hardcodeada post-generación
        ↓
Respuesta al cliente
```

**Importante:** El historial de conversación se guarda en `conversation_history` (dict por session_id). No persiste entre reinicios del servidor.

---

## 6. CÓMO FUNCIONA EL AGENTE DE RECORDATORIOS

```
amuco_reminder_agent.py
        ↓
1. login() → POST a /administrator/login con user/pass de Harold
   → guarda session + CSRF token
        ↓
2. get_quotations() → GET al DataTable interno de cotizaciones
   → filtra: status="quoted", agente_id=HAROLD_AGENT_ID="129", días >= DAYS_THRESHOLD=2
        ↓
3. Por cada cotización:
   get_offer_detail(offer_id)  → extrae producto, cantidad, precio, ETD, incoterm
   get_customer_emails(customer_id)  → extrae emails del cliente del perfil
   detect_language(company_name)  → heurística por nombre de empresa (ES/EN/PT)
        ↓
4. Genera email desde template (EMAIL_TEMPLATES dict, 3 idiomas)
   → sustituye: {customer_name}, {product_name}, {amount}, {currency}, {quote_date}
        ↓
5. send_email(to, subject, body)
   → llama a jarvis_send_email.py del repo Keystone
   → TEST_MODE=True: redirige a TEST_EMAIL (thomasreyesr@gmail.com)
   → DRY_RUN=True: no envía nada, solo imprime
        ↓
6. Notifica a Harold (harold.santiago@amucoinc.com) que se envió el recordatorio
```

**Endpoints internos de kiwi.amucoinc.com que usa el agente:**
- `POST /administrator/login` — autenticación
- `POST /administrator/amuco_customer_request/get_data_table_quotation` — lista cotizaciones
- `GET /administrator/amuco_offers_sent_customers/get_data_by_id?id={id}` — detalle oferta
- `GET /administrator/amuco_customers/view/{id}?popup=show` — emails del cliente

Estos endpoints fueron mapeados manualmente desde DevTools del browser. No hay API oficial.

---

## 7. PROBLEMAS CONOCIDOS Y SOLUCIONES

### Puerto 5001 ocupado (zombie processes)
El problema más común. Si el servidor no arranca o se comporta raro:
```bash
netstat -ano | grep 5001
# Matar cada PID que aparezca:
taskkill /F /PID [numero]
```
Nunca usar `taskkill /f /im python.exe` — mata todos los procesos Python del sistema.

### Respuestas truncadas del chatbot
Si las respuestas se cortan en ~100 caracteres, hay un proceso viejo corriendo.
Matar por PID (ver arriba), reiniciar el servidor, verificar que carga el código nuevo.

### ngrok cambia URL en cada sesión
Cada vez que se abre ngrok, genera una URL nueva. Hay que actualizar el webhook en Twilio manualmente. Para URL fija: contratar ngrok de pago o configurar WhatsApp Business API directo.

### Sandbox de Twilio expira cada 72 horas
Si WhatsApp deja de funcionar, enviar `join determine-begun` al +1 415 523 8886 desde el número de prueba.

### Detector de idioma falla con nombres técnicos (bug conocido)
`detect_language("SINTEPLAST")` devuelve EN en vez de ES. Pendiente mejorar la heurística.

### Gmail API error 403
El token OAuth de Jarvis expiró. Correr el script de autenticación en el repo Keystone.

---

## 8. ARCHIVOS IMPORTANTES

| Archivo | Qué hace |
|---|---|
| `chatbot/rag_chatbot.py` | Servidor principal — Flask + RAG + Gemini |
| `chatbot/rag_indexer.py` | Indexa fichas técnicas en ChromaDB (ejecutar 1 vez) |
| `chatbot/build_catalog.py` | Genera product_catalog.json desde fichas técnicas |
| `reminder_agent/amuco_reminder_agent.py` | Agente de recordatorios standalone |
| `docs/ARRANQUE.md` | Pasos rápidos para levantar el sistema |
| `docs/SESSION_NOTES.md` | Historial de decisiones técnicas por sesión |
| `brief.md` | ⚠️ NO EN GIT — credenciales y contexto del proyecto |
| `.vscode/tasks.json` | Tareas preconfiguradas (F5 para correr el chatbot) |

---

## 9. CONFIGURACIÓN VSCode

El proyecto tiene `.vscode/` configurado:
- **F5** → corre `rag_chatbot.py` en el debugger
- **tasks.json** → tareas para build_catalog, rag_indexer, y reminder_agent
- **settings.json** → Python path apuntando a `/c/Python312/python.exe`

---

## 10. RELACIÓN CON EL ECOSISTEMA KEYSTONE

Este repo es independiente pero se apoya en el repo principal Keystone:
- **Email sender**: usa `agents/2A-CONTADOR/jarvis_send_email.py` del repo Keystone
- **Orquestador**: Jarvis (CLAUDE.md del repo Keystone) puede disparar el agente de recordatorios
- **Credenciales Gmail**: token OAuth vive en el repo Keystone, no aquí

Si no tienes acceso al repo Keystone, el chatbot funciona igual. El agente de recordatorios necesita el email sender — en ese caso, reemplazar la llamada a `jarvis_send_email.py` por `smtplib` con las credenciales que corresponda.

---

## 11. ESTADO ACTUAL (Marzo 2026)

| Componente | Estado | Notas |
|---|---|---|
| Chatbot web | Funcionando | localhost:5001 |
| Chatbot WhatsApp | Funcionando | Twilio Sandbox |
| Agente recordatorios | Funcionando | TEST_MODE=True — envía a Thomas, no al cliente |
| WhatsApp número propio | Pendiente | Requiere aprobación Meta |
| Agente recordatorios producción | Pendiente | Requiere aprobación AMUCO |

---

*Repo creado: 2026-03-20 | Mantenido por Thomas Reyes + Jarvis (Keystone)*
