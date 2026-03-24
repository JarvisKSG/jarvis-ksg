# Protocolo — Email
**Lee este archivo antes de redactar o enviar cualquier correo.**

## Reglas Obligatorias

1. Todo correo a Jeff o Keyser es **bilingüe**: inglés primero, español abajo, separados por `---`
2. Al escribir a jeff.t.bania@gmail.com → dirigirse como "Keyser" o "Keyser Soze", NUNCA "Jeff"
3. Flujo obligatorio: Redactar → QC (agente `qc`) → ✅ Aprobado → Enviar
4. Máximo 3 ciclos de QC antes de escalar a Thomas

## Destinatarios Jeff

Cuando el destinatario principal es Jeff:
- To: jeffbania@gmail.com
- CC: jeff.t.bania@gmail.com, jeff.t1.bania@gmail.com

Cuando el destinatario principal es Keyser:
- To: jeff.t.bania@gmail.com
- CC: jeff.t1.bania@gmail.com, jeffbania@gmail.com

## Envío (Gmail API)

```bash
python tools/send_email.py "to@email.com" "Asunto" "Cuerpo" "cc@email.com"
```

- Cuenta: jarvis.ksg1@gmail.com
- Token OAuth: tools/jarvis_token.json (se renueva automáticamente)

## Protocolo Kaiser (emails de jeff.t.bania@gmail.com)

- Revisar emails entrantes de Kaiser antes de cada sesión
- Si Kaiser pide **información**: buscar datos → responder bilingüe → QC → enviar
- Si Kaiser requiere **decisión u opinión de Thomas**: enviar email de espera a Kaiser + notificar a Thomas
- Escalar a Thomas: aprobaciones de gasto, compromisos de fecha, propuestas nuevas, opiniones personales
