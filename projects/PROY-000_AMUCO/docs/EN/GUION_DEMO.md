# GUION DE PRESENTACION — AMUCO AI Agent System
**Demo para Harold | Viernes 20/03/2026**

---

## ANTES DE EMPEZAR

**Checklist pre-demo (5 min antes):**
```bash
# 1. Verificar que no hay procesos zombie en puerto 5001
netstat -ano | grep 5001

# 2. Si hay procesos, matarlos por PID
# taskkill //F //PID [PID]

# 3. Arrancar el chatbot
cd "C:/Users/thoma/Desktop/Claude/PROY-005_Agente_IA_AMUCO"
/c/Python312/python.exe rag_chatbot.py

# 4. Abrir en el browser: http://localhost:5001
```

**Tener listo:**
- Browser con http://localhost:5001 abierto
- WhatsApp conectado al Sandbox de Twilio
- ngrok corriendo (si se va a demo WhatsApp)

---

## INTRODUCCION (2 min)

> "Harold, what I'm going to show you today is a system made up of two AI agents that work independently but complement each other. Both are designed specifically for AMUCO's Coatings & Paints line.
>
> The first agent answers technical and commercial questions from customers — via web and WhatsApp. The second agent monitors your pending quotes and sends personalized follow-up emails automatically, in the customer's language.
>
> Let me show you how each one works."

---

## PARTE 1 — CHATBOT TECNICO (10 min)

### Que es

> "This is Agent 1. It acts as a technical sales advisor for AMUCO. A customer can ask any question about your products and get an accurate, specific answer — not a generic one."

### Como funciona (explicacion rapida)

> "The system has all 33 product technical data sheets — 412 files — already indexed. When a customer asks something, the agent:
> 1. Classifies the question: is it general or product-specific?
> 2. If general: answers from a catalog of 27 products it has in memory
> 3. If specific: finds the right technical sheet, reads it, and answers with real data
>
> No hallucinations. No invented specs. Real data from your documents."

### Demo en vivo — preguntas sugeridas

**Ronda 1 — Pregunta general (catálogo):**
```
"What products do you have for wood coatings?"
```
> Esperar respuesta. Señalar que el agente menciona varios productos relevantes y ofrece ayuda.

**Ronda 2 — Pregunta especifica:**
```
"Tell me about PLASTIKOTE, what surfaces can I apply it on?"
```
> Señalar: "See how it pulls the actual technical data from the product sheet — application surfaces, coverage, drying time. This is real data from your documents, not generated text."

**Ronda 3 — Seguimiento (multi-turn):**
```
"What's the recommended dilution ratio?"
```
> Señalar: "It remembers the context. The customer doesn't need to repeat which product they were asking about."

**Ronda 4 — Pregunta comercial:**
```
"Is it available in different colors?"
```
> El agente responde con lo que hay en la ficha tecnica.

**Ronda 5 — Cierre:**
```
"Thanks, I'll get back to you"
```
> Señalar: "The agent closes warmly, no robotic responses, no signatures — clean and professional."

### WhatsApp — Twilio Sandbox vs. Production

> "For this demo we're using the **Twilio Sandbox** — a testing environment Twilio provides for developers. It works exactly like real WhatsApp Business, but is limited to numbers that have manually registered by sending an activation code. It's the right tool to validate the agent before investing in the official number."

**How the Sandbox works (worth explaining in the demo):**
- Twilio acts as the intermediary between WhatsApp and our server
- The customer writes to a Twilio number (+1 415 523 8886)
- Twilio forwards the message to our agent via webhook
- The agent responds and Twilio delivers it back to the customer
- All of this happens in milliseconds — the customer doesn't perceive the intermediary

> "What you see in this demo is exactly what a real customer would receive. The only difference is the number the message comes from."

**The path to production — WhatsApp Business API:**

> "For production, the process is registering AMUCO's own number directly with Meta — without Twilio as intermediary if preferred, or keeping it as the API provider. Meta has three options:"

| Option | Description | Approx. time |
|--------|-------------|--------------|
| **WhatsApp Business App** | Free app, manual use only, no automation | Immediate |
| **WhatsApp Business API (via Twilio)** | Full automation, own number, no user limit | 1-2 weeks |
| **WhatsApp Business API (via Meta direct)** | More control, requires Meta Business approval | 2-4 weeks |

> "For this system, the right option is the API — either via Twilio or Meta direct. Once the number is approved, the agent works exactly like in this demo, but from AMUCO's official number with no restrictions."

**What changes technically when going to production:**
- Webhook points to the official number instead of the Sandbox
- No manual activation step required for users
- Unlimited simultaneous conversations
- Ability to add buttons, menus and quick replies (WhatsApp Business features)

---

## PARTE 2 — AGENTE DE RECORDATORIOS (8 min)

### Que es

> "This is Agent 2. It monitors your CRM — kiwi.amucoinc.com — and detects which quotes have been in 'quoted' status for 2 or more days without a response. It then sends a personalized follow-up email to each customer automatically."

### El problema que resuelve

> "Right now, following up on 25+ open quotes manually takes time — and some inevitably fall through the cracks. This agent handles it for you, every day."

### Como funciona (sin API publica)

> "AMUCO's system doesn't have a public API. We mapped the internal endpoints directly from the browser — the same calls the interface makes — and the agent authenticates as a normal user. It reads your quotes, extracts the product, quantity, price, ETD, and the customer's contact info."

**Flujo:**
```
1. Login automatico a kiwi.amucoinc.com
2. Consulta cotizaciones en estado "quoted" con 2+ dias sin respuesta
3. Por cada cotizacion: obtiene producto, cantidad, precio, ETD, emails del cliente
4. Detecta el idioma del cliente (EN / ES / PT)
5. Genera un email personalizado con los datos reales de esa cotizacion
6. Envia el recordatorio
```

### El tono de los emails

> "The emails aren't generic templates. They were trained on your actual emails, Harold — your real style. Personal greeting, specific reference to the product and amount, market context to create urgency, and a direct close."

**Mostrar un email de ejemplo (en pantalla o impreso):**

---
*Example — English client:*

> Subject: Quick follow-up — [Product] / [Company Name]
>
> Hi [Name],
>
> I wanted to follow up on the quote we sent for [Product] — [Qty] MT at $[Price]/MT, total $[Total] (CIF, ETD [Date]).
>
> Given current market conditions, these prices won't hold much longer. I wanted to make sure this is still on your radar.
>
> Happy to answer any questions or adjust the proposal if needed.
>
> Best regards / Saludos cordiales,
> Harold

---

### Modos de operacion

> "The agent has three modes:
> - **DRY RUN**: shows what it would send, sends nothing — for review
> - **TEST MODE**: sends to a test email, not to the real customer — for verification
> - **PRODUCTION**: sends to real customers — requires your approval to activate"

> "Right now it's in TEST MODE. Before going live, you review a few sample emails and confirm the tone is right."

---

## CIERRE (2 min)

> "To summarize — you now have:
>
> 1. A 24/7 technical advisor that answers customer questions on web and WhatsApp, with real data from your product sheets
> 2. An automated follow-up system that monitors your CRM and sends personalized reminders so no quote goes cold
>
> What's still pending before going live:
> - WhatsApp production number: register a business number with Meta (I can guide you through this)
> - Reminder agent production: review 2-3 sample emails and confirm the tone — once approved, it runs daily automatically
>
> Any questions?"

---

## PREGUNTAS FRECUENTES — respuestas preparadas

**"What if the agent gives wrong information?"**
> "The agent only answers from your actual technical sheets. If the information isn't in the document, it says so — it doesn't invent. We also tested all 33 products before today."

**"Can it handle multiple languages?"**
> "Yes. It detects the customer's language from the company name and responds in English, Spanish, or Portuguese. The chatbot answers in whatever language the customer writes in."

**"What does it cost to run?"**
> "The AI model is Google Gemini — paid tier, roughly $0.002 per conversation. For typical usage, under $5/month. Infrastructure is local — no cloud hosting costs."

**"Can I add new products?"**
> "Yes. Upload the new technical sheets to the folder and run the indexer — takes about 5 minutes. The agent picks them up immediately."

**"Is the CRM access secure?"**
> "The agent authenticates exactly as you do — same login, same session. It reads data, it never writes or modifies anything in the system."

---

## NOTAS PARA THOMAS

- Si el demo de WhatsApp falla por ngrok caido: mostrar solo el chatbot web, es suficiente
- Si Gemini da error 429: es rate limit temporal, esperar 30 seg y reintentar
- Puerto 5001 debe estar libre — matar zombies ANTES de arrancar
- Los emails del agente de recordatorios: tener uno impreso como backup por si falla la demo en vivo
