# Wireframe UX-001 — Dashboard de Salud Financiera Keystone
**Agente:** ux_designer | **Fecha:** 2026-03-24
**Usuario objetivo primario:** Jeff Bania (visión ejecutiva)
**Usuario objetivo secundario:** Thomas Reyes (operación diaria)
**Tarea principal (Jeff):** Saber en 5 segundos si el negocio va bien este mes
**Tarea principal (Thomas):** Revisar facturas pendientes y anomalías de proveedores

---

## Decisiones de Arquitectura de Información

### El problema de los 5 grupos de KPIs

El `data_scientist` definió 17 KPIs en 5 grupos. Mostrarlos todos simultáneamente crearía
un dashboard de 17 números que nadie miraría. Solución: **progressive disclosure**.

```
Jeff abre el dashboard
       ↓
Ve SOLO 4 números (Nivel 1) → responde sus 3 preguntas en 5 segundos
       ↓
Si algo llama su atención → click en tab → profundiza (Nivel 2)
       ↓
Si quiere ver una factura específica → click → formulario (Nivel 3)
```

### Qué 4 números van en el Nivel 1 (Above the Fold)

Criterio: los que responden "¿tengo que actuar hoy?"

| Posición | KPI | Color lógica |
|----------|-----|-------------|
| Card 1 | `gasto_total_cop_mes` | emerald si ≤ proyección, amber si +10%, red si +20% |
| Card 2 | `proyeccion_cierre_mes` | emerald/amber/red + etiqueta "ESTIMADO" |
| Card 3 | `facturas_pendientes_cop` | emerald si $0, amber si >0, red si > 30% del gasto total |
| Card 4 | `anomalias_proveedor` (count) | emerald si 0, amber si 1-2, red si ≥3 |

**Por qué NO `burn_rate_diario` en Nivel 1:** burn rate es derivado de gasto_total — ya está implícito. Jeff no piensa en "pesos por día", piensa en "¿voy bien o mal?".

---

## WIREFRAME COMPLETO

### DESKTOP (≥1024px)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔑 KEYSTONE  /  Financial Health Dashboard          [Marzo 2026 ▾]     │
│  Thomas Reyes • Operations Lead                    [Actualizado: 14:32]  │
├──────────────┬──────────────┬──────────────┬──────────────┐             │
│  GASTO MES   │  PROYECCIÓN  │  PENDIENTES  │  ANOMALÍAS   │  ← NIVEL 1 │
│              │              │              │              │             │
│  $2.340.000  │  $3.120.000  │  $480.000    │     3        │             │
│  COP         │  COP ESTIM.  │  COP         │  proveedores │             │
│              │              │              │              │             │
│  [emerald]   │  [amber  ]   │  [amber  ]   │  [red    ]   │             │
│  ↑ vs feb    │  +8% vs meta │  2 facturas  │  revisar ↗   │             │
└──────────────┴──────────────┴──────────────┴──────────────┘             │
                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  [Proveedores]  [Categorías]  [Proyección]  [Ahorros]  [IRS / Jeff]    │
│   tab activo                                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TOP 5 PROVEEDORES — Marzo 2026                                          │
│                                                                          │
│  Ferretería El Tornillo  ████████████████████░░░░  $820.000  (35%)      │
│  Combustibles Del Valle  ████████████░░░░░░░░░░░░  $490.000  (21%)      │
│  Distribuidora Central   ████████░░░░░░░░░░░░░░░░  $340.000  (15%)      │
│  Materiales Barbosa      ██████░░░░░░░░░░░░░░░░░░  $280.000  (12%)      │
│  Servicios Generales     ████░░░░░░░░░░░░░░░░░░░░  $200.000   (9%)      │
│                                                                          │
│  [Ver todos los proveedores →]                                           │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  ⚠  REQUIEREN ATENCIÓN                                          [×]     │
│  [C6-ANOMALÍA] Ferretería El Tornillo — $820.000 (3.2× promedio)        │
│  [C6-ANOMALÍA] Combustibles Del Valle — $490.000 (2.8× promedio)        │
│  [!] 2 facturas sin conciliar — vencen el 28/03/2026                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### PANEL LATERAL — Procesamiento de Recibos (slide-in desde derecha)

El formulario `ReceiptReviewForm` no vive en el dashboard principal.
Se abre como **panel deslizante (slide-over)** cuando Thomas hace click en "Procesar recibo".

```
Dashboard (70% ancho)    │  Procesar Recibo (30% ancho)
                         │
[KPI cards]              │  ┌─────────────────────────┐
                         │  │  Procesar Recibo        │
[Tabs]                   │  │  ─────────────────────  │
                         │  │  [Imagen del recibo]    │
[Gráfica activa]         │  │                         │
                         │  │  [Formulario campos]    │
[Alert bar]              │  │                         │
                         │  │  [Guardar] [Cancelar]   │
                         │  └─────────────────────────┘
```

**Justificación:** El formulario es una tarea de Thomas (operacional), no de Jeff (ejecutivo).
Mantenerlo fuera del dashboard principal evita que Jeff vea complejidad operacional
que no le corresponde. El slide-over mantiene el contexto visual sin cambiar de página.

### MOBILE (<768px)

```
┌───────────────────────────────┐
│ KEYSTONE  Financial Health    │
│ Marzo 2026 ▾         [⟳14:32]│
├─────────────┬─────────────────┤
│ GASTO MES   │ PROYECCIÓN      │
│ $2.340.000  │ $3.120.000 EST. │
│ [emerald]   │ [amber]         │
├─────────────┴─────────────────┤
│ PENDIENTES  │ ANOMALÍAS       │
│ $480.000    │ 3 [red]         │
│ [amber]     │                 │
├─────────────┴─────────────────┤
│ ← Proveedores  Categorías →   │  ← scroll horizontal
├───────────────────────────────┤
│ [Contenido del tab activo]    │
│ Barras horizontales           │
│ adaptadas a ancho móvil       │
├───────────────────────────────┤
│ ⚠ 2 anomalías · 2 pendientes  │
│ [Ver detalles →]              │
└───────────────────────────────┘
```

---

## ESPECIFICACIÓN DE TABS — Nivel 2

### Tab: Proveedores
- **Gráfica:** Bar chart horizontal (barras de colores únicos, no semánticos — son categorías, no estados)
- **Tabla debajo:** Top 5 con columnas Proveedor | Total COP | % | Transacciones
- **Acción:** Click en proveedor → drill-down con historial 90 días (Nivel 3)

### Tab: Categorías
- **Gráfica primaria:** Pie chart con % por OP/ADM/NOM/MF/SP/LT/PROY
- **Gráfica secundaria:** Bar chart apilado por proyecto (PROY-001 a PROY-N)
- **Regla:** Categorías con <3% colapsadas en "Otros" para no saturar el pie

### Tab: Proyección
- **Gráfica:** Line chart con 2 líneas:
  - Línea sólida (emerald): gasto real acumulado día a día
  - Línea punteada (amber): proyección al cierre basada en burn rate
  - Línea de referencia (slate): meta de presupuesto si está definida
- **Label en cada punto:** formato DD/MMM

### Tab: Ahorros
- **KPI card grande:** Total ahorros detectados este mes (emerald)
- **Lista:** Correcciones de proveedor con delta: [Proveedor] cobró $X → registrado $Y → ahorro $Z
- **Acumulado YTD:** Total ahorros del año

### Tab: IRS / Jeff
- **Visible para todos pero relevante principalmente para Jeff**
- **KPI card:** Total deducible USD del mes
- **Tabla:** IRS Category | Monto USD | % Deducible
- **Nota:** "Calculado con TRM del [fecha]. Para declaración final, verificar con contador."

---

## ESTADOS DE LA ALERT BAR

La barra de alertas al fondo del dashboard es persistente pero no invasiva.

```
Estado vacío (emerald, subtle):
  ✅ Todo en orden — sin anomalías ni pendientes urgentes

Estado de advertencia (amber):
  ⚠  1 anomalía detectada · 2 facturas pendientes     [Ver →]

Estado crítico (red):
  🔴 3 anomalías sin revisar · Proyección supera meta   [Revisar ahora →]
```

---

## FLUJO DE INTERACCIÓN — Jeff abre el dashboard por primera vez

```
1. Jeff abre URL → ve Nivel 1 (4 KPI cards) → 5 segundos
2. Card "ANOMALÍAS: 3" está en rojo → Jeff hace click
3. Tab "Proveedores" se activa automáticamente (deep link desde card)
4. Jeff ve la tabla de proveedores con 3 anomalías marcadas [⚠]
5. Jeff puede "Aprobar" o "Escalar a Thomas" desde la misma tabla
6. Si escala → email automático via `email_manager` (bilingüe, QC)
7. Jeff cierra el panel → vuelve al estado normal del dashboard
```

**Total tiempo Jeff: ~90 segundos para revisar el estado del negocio.**

---

## DECISIÓN DE INTEGRACIÓN — Formulario de Recibos vs. Dashboard

**Opción A (elegida):** Slide-over panel — formulario en overlay sobre el dashboard
- ✅ Thomas mantiene contexto visual del dashboard mientras procesa
- ✅ Jeff nunca ve el formulario operacional a menos que acceda explícitamente
- ✅ Compatible con React 18+ `<Dialog>` o `<Sheet>` de Radix/shadcn

**Opción B (descartada):** Página separada /recibos
- ❌ Pierde contexto del dashboard al navegar
- ❌ Más carga de datos al volver

**Opción C (descartada):** Formulario embebido en el mismo scroll
- ❌ Jeff ve complejidad operacional innecesaria
- ❌ Dashboard se vuelve una página de 200+ elementos visibles

---

## ALERTAS P2P GENERADAS

```json
{ "to": "data_scientist",
  "summary": "UX-001 confirma los 4 KPIs del Nivel 1 y la estructura de 5 tabs",
  "action": "Ajustar DATA-001: la proyección debe incluir etiqueta 'ESTIMADO' en el dato entregado, no solo en el dashboard" }

{ "to": "frontend_engineer",
  "summary": "UX-001 listo — estructura del Dashboard de Salud Financiera definida",
  "action": "Handoff spec detallado pendiente para: KpiCard, TabPanel, AlertBar, ProveedorBar, SlideOverForm. Crear como 5 componentes separados (<150L c/u)" }

{ "to": "tester_automation",
  "summary": "Flujo Jeff: 7 pasos definidos en UX-001",
  "action": "TEST-005: E2E Playwright del flujo Jeff (ver anomalía → click card → tab proveedores → aprobar/escalar)" }
```
