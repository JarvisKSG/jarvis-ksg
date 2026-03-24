# UI Mobile Rules — 17 KPIs en Pantalla de iPhone
**Agente:** `mobile_pwa`
**Fecha:** 2026-03-24
**Target:** iPhone SE (375px) → iPhone 15 Pro Max (430px)
**Coordinacion:** `ux_designer` (progressive disclosure), `frontend_engineer` (implementacion)

---

## Principio Rector

El dashboard de Jeff en movil no es una version reducida del desktop — es una **version enfocada**. Jeff en la finca necesita responder 3 preguntas en menos de 10 segundos:
1. ¿Cuanto estamos gastando este mes?
2. ¿Hay algun problema que requiera mi atencion?
3. ¿Vamos bien o mal respecto a la proyeccion?

Todo lo demas es secundario en movil.

---

## Jerarquia de KPIs en Movil (3 niveles)

### Nivel 1 — Above the Fold (visible sin scroll, objetivo offline)
*4 KPIs en 2x2 grid. Caben en 375px sin scroll.*

```
┌─────────────────────────────────────┐
│  KEYSTONE KSG          [sin señal]  │
│  ─────────────────────────────────  │
│  ┌────────────┐  ┌────────────────┐ │
│  │ GASTO MES  │  │  PROYECCION    │ │
│  │ $8.2M COP  │  │ $11.4M [est.] │ │
│  │ ▲ vs marzo │  │ Cierre: Mar 31 │ │
│  └────────────┘  └────────────────┘ │
│  ┌────────────┐  ┌────────────────┐ │
│  │ PENDIENTES │  │   ALERTAS      │ │
│  │ $1.3M COP  │  │    3 items     │ │
│  │ 4 facturas │  │ ⚠ ver detalles │ │
│  └────────────┘  └────────────────┘ │
│                                     │
│  [Ver Proveedores] [Ver Categorias] │
└─────────────────────────────────────┘
```

**Reglas de diseno Nivel 1:**
- Fuente: minimo 24sp para valor principal, 12sp para etiqueta
- Touch target: minimo 44x44pt (regla Apple HIG)
- Semaforo: fondo del card cambia — verde (#E8F5E9), ambar (#FFF8E1), rojo (#FFEBEE)
- Badge "sin señal" visible cuando `navigator.onLine === false` — datos cached con timestamp
- NO incluir graficos en Nivel 1 movil — solo numeros y tendencia (flecha arriba/abajo)

---

### Nivel 2 — Scroll vertical (tabs colapsables)
*5 tabs. En movil: tabs horizontales con scroll, o accordion.*

| Tab | KPIs incluidos en movil | Excluir en movil |
|-----|------------------------|-----------------|
| Proveedores | Top 3 proveedores por gasto, precio vs historico | Tabla completa de N proveedores |
| Categorias | Barra horizontal top 4 categorias por COP | Grafico de dona (muy pequeno en movil) |
| Proyeccion | Linea simplificada: real vs proyectado (2 valores) | Grafico completo con puntos de datos |
| Ahorros | Total ahorros detectados + 1 caso destacado | Lista completa de correcciones |
| IRS/Jeff | % deducible total + total USD deducible | Tabla de mapeo Schedule C completa |

**Reglas de diseno Nivel 2:**
- Tabs: scroll horizontal (no wrap) — visible indicator que hay mas tabs a la derecha
- Accordion alternativo para pantallas muy pequenas (< 375px)
- Cada tab abre en full-screen bottom sheet, no en panel lateral
- Boton "Ver completo en desktop" en footer de cada tab

---

### Nivel 3 — Drill-down (bottom sheet)
*Al tocar cualquier KPI o alerta — abre bottom sheet 85% de altura de pantalla.*

```
┌─────────────────────────────────────┐
│  ____________________________       │
│                                     │
│  ALERTA: Proveedor CEMEX            │
│  ─────────────────────────────────  │
│  Precio actual:    $52,000/bulto    │
│  Precio historico: $47,500/bulto    │
│  Desviacion:       +9.5% ⚠          │
│                                     │
│  Recibo: INV-2026-0234              │
│  Fecha: 22 Mar 2026                 │
│                                     │
│  [Escalar a Thomas] [Marcar OK]     │
│                                     │
└─────────────────────────────────────┘
```

**Reglas de diseno Nivel 3:**
- Bottom sheet: `border-radius: 20px` arriba, handle visual de arrastre
- Swipe down para cerrar (no solo boton X)
- Maximo 2 CTAs en footer del sheet — accion principal + accion secundaria
- Si se abre formulario (ReceiptReviewForm): full screen, no sheet

---

## Los 17 KPIs — Clasificacion Movil

| KPI | Nivel movil | Formato reducido | Offline |
|-----|-------------|-----------------|---------|
| gasto_total_cop_mes | 1 — Card principal | $8.2M COP | SI |
| proyeccion_cierre_mes | 1 — Card principal | $11.4M [est.] | SI |
| facturas_pendientes_cop | 1 — Card | $1.3M / 4 facturas | SI |
| anomalias_count | 1 — Card alerta | 3 alertas | SI |
| burn_rate_diario | 2 — Tab Proyeccion | $XXX k/dia | NO |
| dias_restantes_mes | 2 — Tab Proyeccion | X dias | NO |
| top3_proveedores | 2 — Tab Proveedores | Nombre + total | NO |
| precio_vs_historico | 2 — Tab Proveedores | +/-% por proveedor | NO |
| facturas_por_categoria | 2 — Tab Categorias | Top 4 barras | NO |
| total_iva_cop | 2 — Tab Categorias | $XXX k | NO |
| ahorros_detectados_cop | 2 — Tab Ahorros | $XXX k total | NO |
| errores_proveedor_count | 2 — Tab Ahorros | N errores | NO |
| total_usd_mes | 2 — Tab IRS/Jeff | $X,XXX USD | NO |
| total_deducible_usd | 2 — Tab IRS/Jeff | $X,XXX USD | NO |
| porcentaje_deducible | 2 — Tab IRS/Jeff | XX% | NO |
| proyeccion_impuesto_usa | 2 — Tab IRS/Jeff | $X,XXX USD [est.] | NO |
| vs_mes_anterior | 3 — Drill-down semaforo | +/-% vs mes anterior | NO |

---

## Reglas Tecnicas de Implementacion

### CSS / Tailwind (para `frontend_engineer`)

```css
/* Breakpoints Keystone Mobile */
/* sm: 375px  — iPhone SE */
/* md: 390px  — iPhone 14/15 */
/* lg: 430px  — iPhone 15 Pro Max */

/* Card KPI Nivel 1 */
.kpi-card-mobile {
  min-height: 80px;     /* Suficiente para 44pt touch target + texto */
  padding: 12px 16px;
  border-radius: 12px;
}

/* Valor principal del KPI */
.kpi-value-mobile {
  font-size: clamp(20px, 5vw, 28px);  /* Escala con pantalla */
  font-weight: 700;
  letter-spacing: -0.5px;            /* Mas compacto en movil */
}

/* Badge offline */
.offline-badge {
  font-size: 11px;
  background: #FF6B35;
  color: white;
  border-radius: 4px;
  padding: 2px 6px;
}
```

### Manejo de estado offline (para `frontend_engineer`)

```jsx
// Hook recomendado para todos los componentes que muestran KPIs
const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    const handleOnline = () => { setIsOnline(true); setLastSync(new Date()); };
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => { window.removeEventListener('online', handleOnline); window.removeEventListener('offline', handleOffline); };
  }, []);

  return { isOnline, lastSync };
};
```

---

## Checklist de Aceptacion Movil (antes de QC)

- [ ] Los 4 KPIs de Nivel 1 visibles en iPhone SE (375px) sin scroll
- [ ] Touch targets minimo 44x44pt en todos los elementos interactivos
- [ ] Badge "sin senial" visible cuando offline con timestamp de ultimo sync
- [ ] Bottom sheets cierran con swipe down
- [ ] Tabs de Nivel 2 con scroll horizontal visible
- [ ] Lighthouse Mobile score: Performance >= 90, Accessibility >= 95, PWA = 100
- [ ] Tiempo de carga en red 3G simulada: < 4 segundos (Time to Interactive)
- [ ] Nivel 1 visible desde cache en < 1 segundo

---

*Generado por: `mobile_pwa` | Coordinacion: `ux_designer`, `frontend_engineer` | Pendiente: revision `qc`*
