# GUION DE PRESENTACION — Sistema de Agentes IA AMUCO
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
/c/Python312/python.exe chatbot/rag_chatbot.py

# 4. Abrir en el browser: http://localhost:5001
```

**Tener listo:**
- Browser con http://localhost:5001 abierto
- WhatsApp conectado al Sandbox de Twilio
- ngrok corriendo (si se va a demo WhatsApp)

---

## INTRODUCCION (2 min)

> "Harold, lo que te voy a mostrar hoy es un sistema compuesto por dos agentes de IA que funcionan de forma independiente pero se complementan. Ambos están diseñados específicamente para la línea Coatings & Paints de AMUCO.
>
> El primer agente responde consultas técnicas y comerciales de clientes — por web y por WhatsApp. El segundo monitorea tus cotizaciones pendientes y envía emails de seguimiento personalizados de forma automática, en el idioma del cliente.
>
> Te muestro cómo funciona cada uno."

---

## PARTE 1 — CHATBOT TECNICO (10 min)

### Qué es

> "Este es el Agente 1. Funciona como un asesor técnico de ventas de AMUCO. Un cliente puede hacer cualquier pregunta sobre tus productos y recibir una respuesta precisa y específica — no genérica."

### Cómo funciona (explicación rápida)

> "El sistema tiene todas las fichas técnicas de los 33 productos — 412 archivos — ya indexadas. Cuando un cliente pregunta algo, el agente:
> 1. Clasifica la pregunta: ¿es general o específica de un producto?
> 2. Si es general: responde desde un catálogo de 27 productos que tiene en memoria
> 3. Si es específica: encuentra la ficha técnica correcta, la lee, y responde con datos reales
>
> Sin alucinaciones. Sin especificaciones inventadas. Datos reales de tus documentos."

### Demo en vivo — preguntas sugeridas

**Ronda 1 — Pregunta general (catálogo):**
```
"¿Qué productos tienen para recubrimientos de madera?"
```
> Esperar respuesta. Señalar que el agente menciona varios productos relevantes y ofrece ayuda.

**Ronda 2 — Pregunta específica:**
```
"Cuéntame sobre PLASTIKOTE, ¿en qué superficies se puede aplicar?"
```
> Señalar: "Ves cómo trae los datos reales de la ficha técnica — superficies de aplicación, rendimiento, tiempo de secado. Son datos de tus documentos, no texto generado."

**Ronda 3 — Seguimiento (multi-turn):**
```
"¿Cuál es la dilución recomendada?"
```
> Señalar: "Recuerda el contexto. El cliente no necesita repetir de qué producto estaba preguntando."

**Ronda 4 — Pregunta comercial:**
```
"¿Está disponible en diferentes colores?"
```
> El agente responde con lo que hay en la ficha técnica.

**Ronda 5 — Cierre:**
```
"Gracias, te aviso"
```
> Señalar: "El agente cierra de forma cálida, sin respuestas robóticas, sin firma — limpio y profesional."

### WhatsApp — Twilio Sandbox vs. Producción

> "Para esta demo estamos usando **Twilio Sandbox** — es un entorno de pruebas que Twilio ofrece para desarrolladores. Funciona exactamente igual que WhatsApp Business real, pero está limitado a números que se hayan registrado manualmente enviando un código de activación. Es perfecto para validar que el agente funciona antes de invertir en el número oficial."

**Cómo funciona el Sandbox (para que quede claro en la expo):**
- Twilio actúa como intermediario entre WhatsApp y nuestro servidor
- El cliente escribe a un número de Twilio (+1 415 523 8886)
- Twilio reenvía el mensaje a nuestro agente via webhook
- El agente responde y Twilio lo entrega de vuelta al cliente
- Todo esto ocurre en milisegundos — el cliente no percibe el intermediario

> "Lo que ves en esta demo es exactamente lo que recibiría un cliente real. La única diferencia es el número desde el que llega el mensaje."

**La ruta a producción — WhatsApp Business API:**

> "Para producción, el flujo es registrar el número propio de AMUCO directamente con Meta — sin Twilio como intermediario si se prefiere, o manteniéndolo como proveedor de la API. Meta tiene tres opciones:"

| Opción | Descripción | Tiempo aprox. |
|--------|-------------|---------------|
| **WhatsApp Business App** | App gratuita, para uso manual, sin automatización | Inmediato |
| **WhatsApp Business API (vía Twilio)** | Automatización completa, número propio, sin límite de usuarios | 1-2 semanas |
| **WhatsApp Business API (vía Meta directo)** | Mayor control, requiere aprobación de Meta Business | 2-4 semanas |

> "Para este sistema, la opción correcta es la API — ya sea vía Twilio o Meta directo. Una vez aprobado el número, el agente funciona igual que en esta demo, pero desde el número oficial de AMUCO y sin restricciones de usuarios."

**Qué cambia técnicamente al pasar a producción:**
- El webhook apunta al número oficial en lugar del Sandbox
- Se elimina el paso de activación manual con código
- Capacidad ilimitada de conversaciones simultáneas
- Posibilidad de agregar botones, menús y respuestas rápidas (WhatsApp Business features)

---

## PARTE 2 — AGENTE DE RECORDATORIOS (8 min)

### Qué es

> "Este es el Agente 2. Monitorea tu CRM — kiwi.amucoinc.com — y detecta qué cotizaciones llevan 2 o más días en estado 'quoted' sin respuesta. Luego envía un email de seguimiento personalizado a cada cliente de forma automática."

### El problema que resuelve

> "Hoy en día, hacer seguimiento manual de 25+ cotizaciones abiertas toma tiempo — y algunas inevitablemente se pierden. Este agente lo hace por ti, todos los días."

### Cómo funciona (sin API pública)

> "El sistema de AMUCO no tiene API pública. Mapeamos los endpoints internos directamente desde el navegador — las mismas llamadas que hace la interfaz — y el agente se autentica como un usuario normal. Lee tus cotizaciones, extrae el producto, cantidad, precio, ETD y los datos de contacto del cliente."

**Flujo:**
```
1. Login automático a kiwi.amucoinc.com
2. Consulta cotizaciones en estado "quoted" con 2+ días sin respuesta
3. Por cada cotización: obtiene producto, cantidad, precio, ETD, emails del cliente
4. Detecta el idioma del cliente (EN / ES / PT)
5. Genera un email personalizado con los datos reales de esa cotización
6. Envía el recordatorio — y te notifica a ti que lo hizo
```

### El tono de los emails

> "Los emails no son plantillas genéricas. Se entrenaron con tus correos reales, Harold — tu estilo. Saludo personalizado, referencia específica al producto y monto, contexto de mercado para crear urgencia, y un cierre directo."

**Mostrar un email de ejemplo (en pantalla o impreso):**

---
*Ejemplo — cliente hispanohablante:*

> Asunto: Seguimiento oferta #1234 — Empresa XYZ
>
> Estimado/a [Nombre],
>
> Espero que se encuentre muy bien.
>
> Quería dar seguimiento a la oferta que le compartimos el [Fecha] (Ref. #1234) por un total de USD [Monto].
>
> Dadas las condiciones actuales del mercado, la validez de estas ofertas es bastante corta. Me gustaría conocer sus comentarios para poder avanzar, o revisar si requiere algún ajuste.
>
> Quedo muy atento a su respuesta.
>
> Saludos cordiales,
> Harold Santiago | AMUCO INC.

---

### Modos de operación

> "El agente tiene tres modos:
> - **DRY RUN**: muestra qué enviaría, no envía nada — para revisión
> - **TEST MODE**: envía a un email de prueba, no al cliente real — para verificación
> - **PRODUCCIÓN**: envía a clientes reales — requiere tu aprobación para activar"

> "Ahora mismo está en TEST MODE. Antes de ir a producción, revisas 2-3 emails de muestra y confirmas que el tono está bien."

---

## CIERRE (2 min)

> "En resumen — ahora tienes:
>
> 1. Un asesor técnico disponible 24/7 que responde consultas de clientes por web y WhatsApp, con datos reales de tus fichas técnicas
> 2. Un sistema automatizado de seguimiento que monitorea tu CRM y envía recordatorios personalizados para que ninguna cotización se enfríe
>
> Lo que falta antes de ir a producción:
> - Número de WhatsApp propio: registrar un número de negocio con Meta (te puedo guiar en el proceso)
> - Agente de recordatorios en producción: revisar 2-3 emails de muestra y confirmar el tono — una vez aprobado, corre automáticamente todos los días
>
> ¿Alguna pregunta?"

---

## PREGUNTAS FRECUENTES — respuestas preparadas

**"¿Qué pasa si el agente da información incorrecta?"**
> "El agente solo responde desde tus fichas técnicas reales. Si la información no está en el documento, lo dice — no inventa. Además probamos los 33 productos antes de hoy."

**"¿Puede manejar varios idiomas?"**
> "Sí. Detecta el idioma del cliente por el nombre de la empresa y responde en inglés, español o portugués. El chatbot responde en el idioma en que le escriben."

**"¿Cuánto cuesta operarlo?"**
> "El modelo de IA es Google Gemini — tier de pago, aproximadamente $0.002 por conversación. Con uso típico, menos de $5 al mes. La infraestructura es local — sin costos de hosting en la nube."

**"¿Se pueden agregar productos nuevos?"**
> "Sí. Subes las nuevas fichas técnicas a la carpeta y corres el indexador — toma unos 5 minutos. El agente los toma inmediatamente."

**"¿El acceso al CRM es seguro?"**
> "El agente se autentica exactamente como tú lo haces — mismo login, misma sesión. Lee datos, nunca escribe ni modifica nada en el sistema."

---

## NOTAS PARA THOMAS

- Si el demo de WhatsApp falla por ngrok caído: mostrar solo el chatbot web, es suficiente
- Si Gemini da error 429: es rate limit temporal, esperar 30 seg y reintentar
- Puerto 5001 debe estar libre — matar zombies ANTES de arrancar
- Los emails del agente de recordatorios: tener uno impreso como backup por si falla la demo en vivo
