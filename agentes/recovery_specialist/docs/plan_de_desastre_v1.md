# Plan de Desastre v1 — Keystone KSG
**Agente:** `recovery_specialist`
**Version:** 1.0 | **Fecha:** 2026-03-24
**Objetivo:** Recuperar el sistema completo en menos de **15 minutos** desde cualquier fallo

---

## Clasificacion de Incidentes

| Nivel | Criterio | Tiempo de respuesta | Notifica a |
|-------|----------|---------------------|------------|
| P1 — CRITICO | Caja Negra inaccesible o datos corruptos | < 15 min | Thomas (inmediato) + Jeff (si > 30 min) |
| P2 — ALTO | Dashboard offline, backup fallido, API caida | < 30 min | Thomas (inmediato) |
| P3 — MEDIO | Agente individual falla, Slack/email down | < 2 horas | Thomas (siguiente check) |
| P4 — BAJO | Lentitud de servicio, warning en logs | < 24 horas | Log + revision Thomas proxima sesion |

---

## Escenario 1 — Corrupcion o perdida de Caja Negra (P1)

**Sintoma:** Google Sheets no carga, datos faltantes, filas borradas accidentalmente.

**Cronometro: objetivo < 15 minutos**

```
00:00 — Detectar incidente
├── Abrir Google Sheets y confirmar que el problema es real (no cache)
├── Anotar la fecha y hora exacta del fallo
└── Iniciar cronometro

00:02 — Identificar ultimo backup valido
├── python db_backup.py --status
├── Abrir agentes/recovery_specialist/tools/backup_log.json
└── Localizar el registro mas reciente con status: "VERIFIED"

00:04 — Localizar archivo de backup en Drive
├── Abrir Google Drive → Keystone/Backups/DB/
├── Buscar archivo: caja_negra_[TIMESTAMP].csv.gz.enc
└── Descargar a maquina local

00:06 — Descifrar y descomprimir
├── python db_backup.py --decrypt [archivo.enc]   (pendiente: agregar flag --decrypt al CLI)
├── Alternativa manual:
│   python -c "
│   from agentes.recovery_specialist.tools.db_backup import decrypt_file
│   from pathlib import Path
│   decrypt_file(Path('backup.csv.gz.enc'), Path('backup.csv.gz'))
│   "
└── gzip -d backup.csv.gz → backup.csv

00:09 — Verificar checksum antes de restaurar
├── python -c "from agentes.recovery_specialist.tools.db_backup import sha256_file; from pathlib import Path; print(sha256_file(Path('backup.csv.gz.enc')))"
└── Comparar con el sha256 registrado en backup_log.json — deben ser identicos

00:11 — Restaurar datos en Google Sheets
├── Abrir la hoja mensual afectada en Google Sheets
├── Importar el CSV: Archivo → Importar → Subir → Reemplazar hoja actual
└── Verificar visualmente que los datos se ven correctos (primeras y ultimas 5 filas)

00:14 — Validacion post-restauracion
├── Abrir DASHBOARD_ANUAL y verificar que los totales cuadran
├── Verificar que INDICE_FACTURAS tiene los registros esperados
└── Si todo OK: notificar a Thomas "Restauracion completada, datos al [fecha del backup]"

00:15 — Registrar incidente
└── Agregar entrada en agentes/recovery_specialist/docs/incident_log.md
```

**Si el backup mas reciente tiene mas de 24 horas:**
→ Evaluar con Thomas si usar backup mas antiguo o intentar recuperar desde historial de Google Sheets (la hoja tiene historial de versiones nativo — ver Historial > Ver historial de versiones).

---

## Escenario 2 — Backend/API Python caida (P2)

**Sintoma:** Dashboard React no carga datos, `/api/v1/dashboard/health` retorna error.

```
00:00 — Verificar estado del proceso
├── En servidor: ps aux | grep uvicorn
├── Si no corre: uvicorn main:app --host 0.0.0.0 --port 8000 (o el puerto configurado)
└── Si corre pero da error: revisar logs del proceso

00:05 — Revisar logs de error
├── tail -100 logs/api_error.log
└── Buscar el primer error que aparecio (no los subsecuentes)

00:08 — Reinicio controlado
├── Detener proceso: kill -SIGTERM [PID]
├── Esperar 5 segundos
├── Reiniciar: uvicorn main:app --host 0.0.0.0 --port 8000 &
└── Verificar: curl http://localhost:8000/api/v1/dashboard/health

00:12 — Verificacion completa
├── Abrir dashboard en browser y confirmar que los KPIs cargan
└── Notificar a Thomas y (si aplica) a Jeff que el servicio se restauro
```

---

## Escenario 3 — Backup fallido (P2)

**Sintoma:** Alerta en Slack `#keystone-alertas` de `recovery_specialist`, o backup_log.json muestra status: "INTEGRITY_FAIL".

```
00:00 — Verificar el error exacto
└── python db_backup.py --status → identificar que recurso fallo y el error

00:03 — Intentar backup manual
└── python db_backup.py --resource [sheets|postgres|agents]

00:08 — Si el backup manual falla tambien
├── Verificar BACKUP_ENCRYPTION_KEY en variables de entorno
├── Verificar conectividad a Google Drive (token OAuth vigente)
└── Si es error de Drive: re-autenticar con python agents/2A-CONTADOR/jarvis_drive.py

00:12 — Escalacion
├── Si no se puede corregir en 15 min: notificar a Thomas con el error exacto
└── Registrar en incident_log.md con estado "PENDIENTE RESOLUCION"
```

---

## Escenario 4 — Compromiso de seguridad sospechoso (P1)

**Sintoma:** Actividad inusual en logs, email no autorizado enviado, credenciales expuestas.

```
INMEDIATO — Contener antes de diagnosticar
├── 1. Revocar token OAuth de jarvis.ksg1@gmail.com en Google Account Security
├── 2. Cambiar BACKUP_ENCRYPTION_KEY en el entorno
├── 3. Detener todos los demonios activos (WhatsApp, API backend)
└── 4. Notificar a Thomas y cc: jeff.t.bania@gmail.com

LUEGO — Diagnosticar
├── Revisar logs de security_auditor
├── Revisar agents/2F-SEGURIDAD/logs/security_incidents.md
└── Determinar el vector de ataque antes de reactivar servicios
```

---

## Cronograma de Backups — Vista Semanal

```
LUNES
  03:00 COT — Snapshot semanal /agentes/ → Drive /Keystone/Backups/Agentes/

MARTES a SABADO
  02:00 COT — Export Caja Negra (Sheets CSV) → Drive /Keystone/Backups/DB/
  02:30 COT — pg_dump PostgreSQL (post-cloud) → Drive /Keystone/Backups/DB/

DOMINGO
  02:00 COT — Export Caja Negra (Sheets CSV) → Drive /Keystone/Backups/DB/
  04:00 COT — pg_dump PostgreSQL FULL semanal → Drive /Keystone/Backups/DB/Weekly/

DIARIO (cualquier hora)
  recovery_specialist verifica backup_log.json
  Si ultimo backup > 25 horas: alerta Slack #keystone-alertas
```

**Politica de retencion:**
- Backups diarios: 30 dias
- Backups semanales: 12 semanas (3 meses)
- Backups mensuales (del primer dia de cada mes): 12 meses

---

## Configuracion de Cron (Linux/Mac) o Task Scheduler (Windows)

```bash
# Crontab entry — backup diario Caja Negra a las 2am hora Colombia (UTC-5 = 07:00 UTC)
0 7 * * * cd /path/to/jarvis && python agentes/recovery_specialist/tools/db_backup.py --resource sheets >> logs/backup_daily.log 2>&1

# Snapshot semanal de agentes (lunes 3am COT = 08:00 UTC)
0 8 * * 1 cd /path/to/jarvis && python agentes/recovery_specialist/tools/db_backup.py --resource agents >> logs/backup_weekly.log 2>&1
```

```python
# Windows Task Scheduler — ejecutar via Python
# Trigger: Diario a las 02:00
# Accion: python "C:\ruta\jarvis\agentes\recovery_specialist\tools\db_backup.py" --resource sheets
```

---

## Contactos de Emergencia

| Rol | Persona | Contacto | Cuando llamar |
|-----|---------|----------|---------------|
| Operations Lead | Thomas Reyes | thomasreyesr@gmail.com | Siempre primero — P1, P2, P3 |
| Owner / Principal | Jeff Bania | jeffbania@gmail.com | Solo P1 si Thomas no responde en 30 min |
| Jarvis (IA) | recovery_specialist | jarvis.ksg1@gmail.com | Alertas automaticas P1/P2 |

---

## Checklist de Prueba Mensual (Restauracion de Punto Cero)

El primer lunes de cada mes, ejecutar:

- [ ] Descargar el backup mas reciente de Drive
- [ ] Verificar SHA-256 contra backup_log.json
- [ ] Descifrar y descomprimir en carpeta temporal aislada
- [ ] Confirmar que el CSV/SQL es legible y tiene el numero esperado de registros
- [ ] Registrar resultado en incident_log.md como "DRILL-[MES]-[AÑO]: PASS/FAIL"
- [ ] Si FAIL: escalar a Thomas inmediatamente — el backup no sirve si no se puede restaurar

---

*Generado por: `recovery_specialist` | Pendiente validacion: `security_auditor` (rutas de almacenamiento) + `qc`*
