# ARRANQUE — Pasos para dejar todo funcional

---

## CHATBOT WEB (localhost:5001)

Solo necesitas esto para demos locales o pruebas.

**1. Abrir VSCode en esta carpeta**
**2. Terminal > Run Task → `Arrancar Chatbot (limpio)`**

Eso mata zombies del puerto 5001 y arranca el servidor automáticamente.

O manualmente en terminal:
```bash
netstat -ano | grep 5001
# Si hay PIDs: taskkill //F //PID [PID]
/c/Python312/python.exe chatbot/rag_chatbot.py
```

**3. Abrir en el browser:** http://localhost:5001

---

## CHATBOT WHATSAPP (Twilio Sandbox)

Hacer esto CADA VEZ que quieras recibir mensajes por WhatsApp.

**Paso 1 — Arrancar el chatbot** (igual que arriba, debe estar corriendo)

**Paso 2 — Abrir ngrok en una terminal separada:**
```bash
ngrok http 5001
```
Copiar la URL que aparece, ejemplo:
```
https://coleman-scotomatous-jann.ngrok-free.app
```

**Paso 3 — Actualizar webhook en Twilio:**
1. Ir a https://console.twilio.com
2. Messaging → Try it out → Send a WhatsApp message
3. Sandbox settings
4. En "When a message comes in" pegar: `https://[tu-url-ngrok]/whatsapp`
5. Guardar

**Paso 4 — Activar el Sandbox en tu WhatsApp** (solo si pasaron +72 horas):
- Mandar `join determine-begun` al +1 415 523 8886

> La URL de ngrok cambia cada vez que lo reinicias. Siempre actualizar Twilio con la nueva.

---

## AGENTE DE RECORDATORIOS DE COTIZACIONES

**Modo simulacion (sin envios reales):**
```bash
/c/Python312/python.exe reminder_agent/amuco_reminder_agent.py
```
Muestra qué cotizaciones están pendientes y qué emails habría enviado.

**Modo test (envia a thomasreyesr@gmail.com, NO al cliente):**
- `DRY_RUN = False` y `TEST_MODE = True` en el script (ya configurado así)
```bash
/c/Python312/python.exe reminder_agent/amuco_reminder_agent.py
```

**Modo produccion (envia a clientes reales):**
- Requiere aprobación de AMUCO antes de activar
```bash
/c/Python312/python.exe reminder_agent/amuco_reminder_agent.py --send
```

> Cuando se envía un recordatorio al cliente, Harold recibe automáticamente una notificación a harold.santiago@amucoinc.com.

---

## RESUMEN RAPIDO

| Qué quiero hacer | Qué necesito abrir |
|------------------|--------------------|
| Chatbot web | Solo el chatbot (`rag_chatbot.py`) |
| Chatbot WhatsApp | Chatbot + ngrok + actualizar Twilio |
| Agente de emails | Solo `amuco_reminder_agent.py` |
| Todo junto | Chatbot + ngrok + Twilio (el agente corre aparte cuando quieras) |
