# Guia de Implementacion — Inventario-Barbosa
**Workflow:** Sincronizacion de Inventario de Materiales — PROY-001
**Agente:** n8n_engineer
**Fecha:** 2026-03-23

---

## 1. Nodos utilizados

| # | Nombre del nodo | Tipo | Proposito |
|---|----------------|------|-----------|
| 1 | Webhook — Recibir Payload | `n8n-nodes-base.webhook` | Punto de entrada HTTP POST desde la app de campo |
| 2 | Validar Payload | `n8n-nodes-base.if` | Verifica que `fecha`, `proyecto` y `materiales` esten presentes y no vacios |
| 3 | Transformar Materiales | `n8n-nodes-base.code` (JS) | Aplana el array de materiales, calcula `total_cop = cantidad * costo_unitario`, agrega `timestamp_sync` |
| 4 | Split In Batches | `n8n-nodes-base.splitInBatches` | Procesa maximo 10 materiales por lote para no saturar la Sheets API |
| 5 | Append a Google Sheets | `n8n-nodes-base.googleSheets` | Inserta cada fila de material en la hoja `Inventario_Materiales` |
| 6 | Construir Respuesta OK | `n8n-nodes-base.code` (JS) | Arma la respuesta final: `{ status, records_processed, timestamp }` |
| 7 | Respuesta Error Validacion | `n8n-nodes-base.code` (JS) | Responde con error estructurado si el payload no pasa la validacion |
| 8 | Error Trigger | `n8n-nodes-base.errorTrigger` | Se activa si cualquier nodo del workflow falla en runtime |
| 9 | Formatear Alerta de Error | `n8n-nodes-base.code` (JS) | Construye el mensaje estandar Keystone: `[n8n ERROR] Workflow: ... | Node: ... | Message: ... | Time: ...` |
| 10 | Notificar Error a Thomas | `n8n-nodes-base.httpRequest` | Envia la alerta al endpoint de email_manager (jarvis_send_email.py) |
| 11 | Sticky Note — Documentacion | `n8n-nodes-base.stickyNote` | Referencia interna del flujo, URL del webhook y credenciales necesarias |

---

## 2. Credenciales necesarias

### 2.1 Google Sheets OAuth2
- **Nombre en n8n:** `Keystone Google Sheets`
- **Tipo:** `googleSheetsOAuth2Api`
- **Como crear:**
  1. En n8n ir a `Credentials > New > Google Sheets OAuth2 API`
  2. Usar el proyecto de Google Cloud que tiene Sheets API habilitada (proyecto ID: 8521263338 segun MEMORY.md)
  3. Credenciales OAuth: usar las mismas de `~/.claude/gdrive-credentials.json`
  4. Autorizar con la cuenta `jarvis.ksg1@gmail.com`
- **Documento destino:** ID del spreadsheet de inventario (configurar en la variable `SHEETS_DOC_ID`)

### 2.2 Variable de entorno n8n
- `SHEETS_DOC_ID` — ID del Google Sheets donde se acumulan los registros de inventario
  - Puede ser el mismo spreadsheet de contabilidad Keystone o uno dedicado
  - Configurar en n8n: `Settings > Variables > New Variable`

### 2.3 Endpoint de notificacion de errores
- El nodo "Notificar Error a Thomas" apunta a `https://api.jarvis.keystone.internal/notify`
- **Reemplazar** por una de estas opciones segun infraestructura disponible:
  - Nodo `Gmail` con credencial `jarvis.ksg1@gmail.com` (recomendado para produccion)
  - Llamada directa a `python agents/2A-CONTADOR/jarvis_send_email.py` via nodo `Execute Command`
  - Webhook a Slack si el canal #alertas esta configurado

---

## 3. Hoja de destino en Google Sheets

**Nombre de la hoja:** `Inventario_Materiales`

Crear la hoja con estos encabezados en la fila 1 (exactamente en este orden):

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| fecha | proyecto | nombre | cantidad | unidad | costo_unitario | total_cop | reportado_por | timestamp_sync |

- `fecha`: string YYYY-MM-DD
- `proyecto`: string (ej: "PROY-001")
- `nombre`: string (ej: "Cemento")
- `cantidad`: numero
- `unidad`: string (ej: "bultos", "metros")
- `costo_unitario`: numero entero COP
- `total_cop`: numero entero COP (calculado por el workflow)
- `reportado_por`: string
- `timestamp_sync`: ISO 8601 UTC (ej: "2026-03-23T14:30:00.000Z")

---

## 4. Como importar el workflow

1. Abrir n8n
2. Ir a `Workflows > Import from file`
3. Seleccionar `agentes/n8n_engineer/workflows/inventario_barbosa_sync.json`
4. Configurar la credencial `Keystone Google Sheets` en el nodo "Append a Google Sheets"
5. Establecer la variable `SHEETS_DOC_ID`
6. Activar el workflow (toggle superior derecho)

---

## 5. Como probar

### Prueba 1 — Payload valido (happy path)
```bash
curl -X POST https://<tu-n8n-host>/webhook-test/inventario-barbosa \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2026-03-23",
    "proyecto": "PROY-001",
    "materiales": [
      { "nombre": "Cemento", "cantidad": 10, "unidad": "bultos", "costo_unitario": 28000 },
      { "nombre": "Varilla", "cantidad": 5, "unidad": "metros", "costo_unitario": 15000 }
    ],
    "reportado_por": "Operario Campo"
  }'
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "records_processed": 2,
  "timestamp": "2026-03-23T14:30:00.000Z"
}
```

**Verificar en Sheets:** deben aparecer 2 filas nuevas con `total_cop` de 280000 y 75000 respectivamente.

### Prueba 2 — Payload invalido (sin campo `fecha`)
```bash
curl -X POST https://<tu-n8n-host>/webhook-test/inventario-barbosa \
  -H "Content-Type: application/json" \
  -d '{
    "proyecto": "PROY-001",
    "materiales": [{ "nombre": "Cemento", "cantidad": 10, "unidad": "bultos", "costo_unitario": 28000 }]
  }'
```

**Respuesta esperada:**
```json
{
  "status": "error",
  "message": "Payload invalido. Se requieren: fecha (string), proyecto (string), materiales (array no vacio).",
  "timestamp": "2026-03-23T14:30:01.000Z"
}
```

**Verificar:** ningun registro debe escribirse en Sheets.

### Prueba 3 — Material con campos faltantes
```bash
curl -X POST https://<tu-n8n-host>/webhook-test/inventario-barbosa \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2026-03-23",
    "proyecto": "PROY-001",
    "materiales": [
      { "nombre": "Cemento", "cantidad": 10 }
    ],
    "reportado_por": "Operario Campo"
  }'
```

**Resultado esperado:** el Code node lanza excepcion → Error Trigger se activa → Thomas recibe alerta.

### Prueba 4 — Batch grande (mas de 10 materiales)
Enviar un array de 15 materiales. El nodo Split In Batches debe procesarlos en 2 lotes (10 + 5) y al final `records_processed` debe ser 15.

---

## 6. Casos limite conocidos

| Caso | Comportamiento actual | Recomendacion |
|------|----------------------|---------------|
| `materiales` es array vacio `[]` | IF node rechaza (condicion `length > 0` falla) → respuesta 400 | Correcto por diseno |
| `cantidad` o `costo_unitario` son strings numericos ("10") | `Number()` los convierte correctamente | Aceptado |
| `costo_unitario` es 0 | `total_cop` resulta 0 — se escribe igualmente | Valido (material gratuito o donado) |
| Finca envia el mismo reporte dos veces | Se escriben filas duplicadas — no hay deduplicacion por diseno | Para produccion: agregar logica de check por `fecha + nombre + reportado_por` antes del append |
| Google Sheets API rate limit (100 req/100s) | Con max 10 por batch y payloads diarios el riesgo es minimo | Si el volumen crece, agregar nodo Wait (1s) entre batches |
| Campo `reportado_por` ausente | El Code node lo defaultea a `'Desconocido'` — no falla | Correcto |
| n8n fuera de linea durante el envio del webhook | La app de campo recibira timeout — no hay mecanismo de retry en n8n | Recomendado: configurar retry en la app de campo (3 intentos con backoff exponencial) |
| Token OAuth de Google Sheets expirado | n8n renueva automaticamente si el refresh token es valido | Verificar que el token no haya sido revocado en Google Cloud |

---

## 7. Diagrama de flujo (texto)

```
[POST /webhook/inventario-barbosa]
         |
         v
[Validar Payload — IF]
    |           |
  TRUE        FALSE
    |           |
    v           v
[Transformar   [Respuesta Error
 Materiales]    Validacion 400]
    |
    v
[Split In Batches — max 10]
    |
    v
[Append a Google Sheets]
    |
    v
[Construir Respuesta OK]
    |
    v
[HTTP Response: { status, records_processed, timestamp }]

--- Rama de error (cualquier nodo) ---

[Error Trigger]
    |
    v
[Formatear Alerta de Error]
    |
    v
[Notificar Error a Thomas — HTTP Request]
```

---

## 8. Notas de produccion

- **Timezone:** El workflow esta configurado en `America/Bogota` (UTC-5). El campo `timestamp_sync` se almacena en UTC para consistencia.
- **Activacion:** El webhook solo funciona cuando el workflow esta activo (toggle ON). En modo test usar la URL `/webhook-test/`.
- **Logs:** n8n guarda todas las ejecuciones fallidas (`saveDataErrorExecution: all`) y la ultima exitosa (`saveDataSuccessExecution: last`). Revisar en `Executions` del workflow.
- **Escalacion:** Si el Error Trigger se activa mas de 3 veces en un dia, escalar a Thomas y revisar si la app de campo cambio el schema del payload.
