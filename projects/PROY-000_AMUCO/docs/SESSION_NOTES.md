# PROY-005 — Estado de Sesión
Última actualización: 2026-03-19 (sesión 3)

---

## LO QUE ESTÁ HECHO

### Infraestructura
- [x] Slack conectado — canal: #proyecto-agenteia-atencion-al-cliente (ID: C0AMKTWDCLD)
- [x] Bot Jarvis invitado al canal, token funcionando
- [x] Brief del proyecto en `brief.md` (datos sensibles, NO en git)
- [x] PROY-005 registrado en `registro_proyectos.md` como prioridad #1

### Acceso a kiwi.amucoinc.com
- [x] Login automático funcionando (sesión + CSRF)
- [x] Endpoint de cotizaciones mapeado: `/administrator/amuco_customer_request/get_data_table_quotation`
- [x] Endpoint de detalle de oferta: `/administrator/amuco_offers_sent_customers/get_data_by_id?id={offer_id}`
- [x] Perfil de cliente (emails): `/administrator/amuco_customers/view/{customer_id}?popup=show`
- [x] Harold agent ID: **129**
- [x] 25 cotizaciones quoted de Harold, 19 con 2+ días sin respuesta

### Agente de Recordatorios (`amuco_reminder_agent.py`)
- [x] Script construido y probado
- [x] TEST_MODE funciona — envía a thomasreyesr@gmail.com
- [x] DRY_RUN disponible para simulación sin envíos
- [x] Detección de idioma (EN/ES/PT) por nombre de empresa
- [x] Templates bilingües básicos (EN/ES/PT)
- [x] Datos disponibles por cotización: producto, cantidad, precio/unit, total, incoterm, ETD, comentario proveedor, emails cliente

### SharePoint
- [x] Bearer token funciona (extraído del browser DevTools de la sesión de Harold)
- [x] Carpeta mapeada: `/sites/Amuco/Shared Documents/Sales/AMUCO Archivos Comerciales/02 COMERCIAL/07 DOCUMENTOS PRODUCTOS/04 LINEA COATINGS & PAINTS`
- [x] **412 archivos descargados** de 33 productos (PDFs + DOCX)
- [x] Organizados en subcarpetas por producto en `fichas_tecnicas/`
- Productos sin archivos: Lithium Hydroxi, Silica, Trisopropanolamine TIPA 85%, Formalin 37%

### Chatbot RAG — FUNCIONANDO ✓ (sesión 3: todos los bugs resueltos)
- [x] Fichas técnicas indexadas: 709 chunks en ChromaDB
- [x] Embeddings: Gemini `gemini-embedding-001`
- [x] Chatbot web Flask en localhost:5001 (`rag_chatbot.py`)
- [x] Modelo generativo: `gemini-2.5-flash` (API key de pago)
- [x] Clasificador local: GENERAL vs SPECIFIC (sin llamada a API)
- [x] Preguntas generales → catálogo en system_instruction, respuesta conversacional
- [x] Preguntas específicas → PDF completo del producto cargado inline
- [x] Historial multi-turn correcto (list[Content] con roles user/model)
- [x] Firma "AMUCO Technical Support Team" eliminada — _strip_signature() server-side
- [x] Cierre de conversación → frase cálida, sin firma
- [x] Guion de prueba completo pasado: rondas 1-3 y 5 OK

**Bugs resueltos en sesión 3:**
1. Firma aparecía siempre → `_strip_signature()` con regex
2. Catálogo no llegaba a Gemini → movido al `system_instruction` (f-string)
3. Historial como texto plano confundía al modelo → convertido a `list[types.Content]` con roles
4. 28 procesos zombie en puerto 5001 → matar por PID antes de arrancar
5. WhatsApp endpoint usaba `ask_gemini()` inexistente → corregido a `ask_gemini_specific()`
6. `response.text` podía ser None → fallback de texto + strip

---

## LO QUE FALTA

### Demo Viernes 20/03/2026
- [ ] Guión de presentación en inglés para Harold
- [ ] Preparar demo en vivo (casos de uso con datos reales)
- [ ] Ensayo del flujo completo

### Agente de Recordatorios — mejoras pendientes
- [ ] Actualizar templates con datos reales de cada cotización
- [ ] Resolver IDs de puertos (origen/destino) a nombres reales
- [ ] Manejar cotizaciones con múltiples ofertas
- [ ] Agregar lógica anti-duplicado
- [ ] Notificación interna a Harold cuando se envía un recordatorio

### Chatbot — mejoras post-demo
- [ ] Configurar Twilio WhatsApp Sandbox + ngrok
- [ ] Probar respuestas en EN/PT
- [ ] Correos reales de Harold para ajustar tono/estilo

---

## ARRANCAR EL SERVIDOR (IMPORTANTE)

```bash
# 1. Matar procesos zombie primero
netstat -ano | grep 5001
# Para cada PID que aparezca: taskkill //F //PID [PID]

# 2. Arrancar limpio
cd "C:/Users/thoma/Desktop/Claude/agents/3A-PROYECTOS/PROY-005_Agente_IA_AMUCO"
"/c/Python312/python.exe" rag_chatbot.py
```

**NUNCA usar `taskkill /f /im python.exe`** — en bash no funciona bien y deja zombies.
Matar siempre por PID usando `netstat -ano | grep 5001`.

---

## DECISIONES TÉCNICAS TOMADAS

| Decisión | Razón |
|----------|-------|
| Sin API oficial — usar endpoint interno | kiwi.amucoinc.com no tiene API pública |
| Catálogo en system_instruction | Evita turnos falsos en el historial que confunden al modelo |
| Historial como list[Content] | Formato correcto multi-turn de la API de Gemini |
| _strip_signature() server-side | El modelo ignora instrucciones de no firmar — más confiable limpiar en código |
| Paid API key (gemini-2.5-flash) | Free tier: 20 req/día, agotado. Paid tier: sin límite práctico |
| Python 3.12 | NO usar python3 que apunta a 3.13 — usar `/c/Python312/python.exe` |
| Puerto 5001 | Puerto 5000 tenía conflictos con otros servicios |

---

## ARCHIVOS CLAVE

| Archivo | Descripción |
|---------|-------------|
| `brief.md` | Contexto completo del proyecto (SENSIBLE — no en git) |
| `amuco_reminder_agent.py` | Script agente de recordatorios (funcional, TEST_MODE) |
| `rag_chatbot.py` | Chatbot RAG principal (FUNCIONANDO) |
| `rag_indexer.py` | Indexador — ejecutar solo si se agregan nuevas fichas |
| `build_catalog.py` | Genera product_catalog.json — ejecutar si cambian productos |
| `product_catalog.json` | Catálogo de 27 productos (usado en system_instruction) |
| `chroma_db/` | Base vectorial con 709 chunks indexados |
| `fichas_tecnicas/` | 412 archivos organizados por producto |

---

## STACK TÉCNICO

```
Python 3.12 → /c/Python312/python.exe
Flask → servidor web en localhost:5001
ChromaDB → búsqueda vectorial local (chroma_db/)
Gemini API (paid) → AIzaSyA4pjEJKl59n98asW-XwcfWHf-U2n7iujc
  - Embeddings: gemini-embedding-001
  - Generación: gemini-2.5-flash
```

---

## CONTEXTO TÉCNICO RÁPIDO

```python
# Login kiwi
AMUCO_URL = "https://kiwi.amucoinc.com"
AMUCO_USER = "harold.santiago@amucoinc.com"
HAROLD_AGENT_ID = "129"

# Slack
SLACK_CHANNEL = "C0AMKTWDCLD"  # #proyecto-agenteia-atencion-al-cliente
```
