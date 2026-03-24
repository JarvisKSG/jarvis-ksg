# Protocolo — QC Capas de Validación C1–C7
**Referenciado por el agente qc. Lee este archivo al iniciar una validación.**

## Pre-Scan (obligatorio antes de aplicar capas)

Leer el output completo de una vez antes de evaluar. Construir imagen del conjunto:
- Volumen (cuántos registros, campos, hojas)
- Rango de valores (mín, máx, promedio) → alimenta C6
- Patrón de un registro normal
- Cualquier anomalía visual obvia

## C1 — Fidelidad al Pedido (más crítica)

Comparar la instrucción original con lo entregado:
- ¿Se hizo exactamente lo que se pidió — ni más ni menos?
- ¿Falta alguna parte del pedido?
- ¿Se malinterpretó algo?

Un output técnicamente perfecto que no responde el pedido es rechazo inmediato C1.

## C2 — Completitud de Campos

- Todos los campos requeridos presentes y llenos
- Combinaciones lógicas coherentes: Status "Pagado" requiere Método de Pago lleno; Status "Completado" requiere fecha de cierre

## C3 — Lógica Temporal y de Estado

- Sin fechas futuras marcadas como pagadas, completadas o facturadas
- Sin proyecciones presentadas como hechos históricos sin etiqueta explícita
- Items pendientes en fechas pasadas requieren explicación documentada

## C4 — Consistencia Matemática

- Totales, subtotales y fórmulas aritméticamente correctos
- TRM: usar la tasa provista por Jarvis en el contexto de la tarea
  - Auditorías históricas 2025: 1 USD = 3,994 COP (promedio anual IRS 2025)
  - Operaciones 2026: Jarvis debe proveer TRM actual — no asumir tasa fija
  - Si no se proveyó TRM y la tarea involucra conversiones USD 2026: solicitar antes de validar
- Cifras de resumen/dashboard coinciden con registros de detalle

## C5 — Detección de Duplicados

- Sin filas repetidas, facturas duplicadas, o registros procesados dos veces en el mismo lote

## C6 — Detección de Anomalías

Calcular promedio del lote. Marcar como `[C6-ANOMALÍA]` cualquier item ≥5x el promedio.

Cálculo explícito obligatorio:
```
Promedio del lote = suma de todos los items / cantidad de items
Ratio = item sospechoso / promedio
→ Si ratio ≥ 5x → [C6-ANOMALÍA]
```

Las anomalías **no bloquean** la aprobación — requieren justificación de Thomas.
Excepción: si la anomalía es claramente un error de dígitos (ej. ceros de más) → error crítico.

## C7 — Consistencia de Estilo

- Formato de fecha: DD/MM/AAAA
- Protocolo de idioma:
  - Comunicación interna entre agentes (JSON, feedback correctivo): inglés
  - Reportes y aprobaciones finales a Thomas: español
- Estructura y tono consistentes con los estándares Keystone

## Formato de Reportes

### Rechazo
```
❌ QC RECHAZO — [Agente] — [DD/MM/AAAA HH:MM]
──────────────────────────────────────────────
ERRORES CRÍTICOS (bloquean aprobación):
  [C1] [descripción exacta]
  [C3] Fila 12, columna "Estado": fecha 2026-09-15 (futura) marcada como "Pagado"

ADVERTENCIAS (requieren justificación de Thomas):
  [C6-ANOMALÍA] Factura #0032 — 4,500,000 COP — 7x promedio del lote (643,000 COP)

ACCIÓN REQUERIDA:
  1. [corrección específica]
  2. [corrección específica]

Ciclo: [N]/3 antes de escalación a Thomas.
──────────────────────────────────────────────
```

### Aprobación
```
✅ QC APROBADO — [Agente] — [DD/MM/AAAA HH:MM]
──────────────────────────────────────────────
Capas: C1 ✓  C2 ✓  C3 ✓  C4 ✓  C5 ✓  C6 ✓  C7 ✓
Advertencias registradas: [N]
APROBADO — [Agente] puede proceder con entrega final.
──────────────────────────────────────────────
```

## Escalación (ciclo 4)

```json
{
  "requesting_agent": "qc",
  "request_type": "escalate_to_thomas",
  "payload": {
    "agent": "[nombre del agente]",
    "task": "[descripción de la tarea]",
    "persistent_error": "[error exacto que persiste]",
    "cycles_attempted": 3,
    "decision_needed": "[qué necesita decidir Thomas para desbloquear]"
  }
}
```
