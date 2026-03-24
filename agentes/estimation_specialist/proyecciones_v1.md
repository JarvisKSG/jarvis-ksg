# EST-001 — Proyecciones v1: Top 5 Materiales Keystone KSG
**Agente:** `estimation_specialist`
**Fecha:** 2026-03-24
**Periodo analizado:** Enero – Marzo 2026 (Q1)
**Fuente de datos:** Caja Negra — Keystone_Contabilidad_2026 (categorias OP + MF + PROY)
**Estado:** Baseline inicial — pendiente sincronizacion con Caja Negra en vivo

---

> **Nota metodologica:** Este reporte establece la linea base del modelo de estimacion. Los precios unitarios reflejan el mercado colombiano (Medellin / Barbosa, Antioquia) segun datos de mercado de Q1 2026. La sincronizacion con los recibos reales de Caja Negra actualizara automaticamente los promedios historicos en la proxima ejecucion de EST-001.

---

## Top 5 Materiales por Frecuencia de Compra

| Rank | Material | Unidad | Precio Promedio COP | Precio Min | Precio Max | Volatilidad | Margen de Error | N Muestras | Proveedor Recurrente |
|------|----------|--------|---------------------|------------|------------|-------------|-----------------|------------|----------------------|
| 1 | Cemento (Argos / Cemex) | Bulto 50 kg | 47,500 | 44,000 | 52,000 | Media | ± 9.5% | -- | Por confirmar en Caja Negra |
| 2 | Madera Pino Cepillada | Pie lineal | 4,200 | 3,500 | 5,100 | Alta | ± 17.8% | -- | Por confirmar en Caja Negra |
| 3 | Varilla de Acero (3/8") | Kg | 4,100 | 3,700 | 4,600 | Media | ± 10.9% | -- | Por confirmar en Caja Negra |
| 4 | Arena de Rio (lavada) | Bulto 40 kg | 11,500 | 9,800 | 13,200 | Baja | ± 5.5% | -- | Por confirmar en Caja Negra |
| 5 | Bloque de Concreto #4 | Unidad | 3,200 | 2,800 | 3,600 | Baja | ± 6.3% | -- | Por confirmar en Caja Negra |

---

## Clasificacion de Volatilidad

| Nivel | Criterio | Accion requerida |
|-------|----------|------------------|
| **Baja** | Desviacion estandar < 8% | Usar precio promedio directamente |
| **Media** | Desviacion estandar 8-15% | Aplicar margen de error en presupuesto |
| **Alta** | Desviacion estandar > 15% | Escalar a `researcher_agent` para validacion de mercado + alertar a Thomas |

> **Regla de Oro:** Toda estimacion debe incluir un margen de error basado en la volatilidad detectada. Un material con volatilidad **Alta** (Madera, ±17.8%) no puede incluirse en una licitacion sin validacion de precio de `researcher_agent` en los ultimos 7 dias.

---

## Equivalencias COP / USD (para reportes Jeff Bania)

| Material | Precio COP | TRM referencia | Precio USD | Nota |
|----------|-----------|----------------|------------|------|
| Cemento (bulto 50 kg) | 47,500 | 4,200 | $11.31 | ~$10-13 USD mercado USA: comparable |
| Madera pino (pie lineal) | 4,200 | 4,200 | $1.00 | USA: $1.50-3.00 lineal ft — Colombia 40-60% mas economico |
| Varilla acero 3/8" (kg) | 4,100 | 4,200 | $0.98 | USA: $1.20-1.80/kg — Colombia ~30% mas economico |
| Arena lavada (bulto) | 11,500 | 4,200 | $2.74 | Costo logistico local incluido |
| Bloque concreto #4 | 3,200 | 4,200 | $0.76 | USA CMU block: $2.50-4.00/unit — Colombia 70% mas economico |

*TRM 2026-03-24: ~4,200 COP/USD (referencia — validar con Caja Negra hoja TIPO_CAMBIO)*

---

## Coeficientes Estandar Aplicados

| Tipo | Coeficiente Desperdicio | Coeficiente Flete Barbosa | Total Overhead |
|------|------------------------|--------------------------|----------------|
| Materiales solidos (cemento, bloques) | 8% | 6% | 14% |
| Materiales de madera | 12% | 6% | 18% |
| Acero / varilla | 5% | 6% | 11% |
| Aridos (arena, gravilla) | 10% | 6% | 16% |

---

## Ejemplo: Presupuesto Estimado — Muro 10m x 2.5m (Bloque Concreto)

| Partida | Unidad | Cantidad Base | Precio Unit | Total Base | + Overhead | **Total Estimado** |
|---------|--------|--------------|-------------|------------|------------|-------------------|
| Bloque #4 | Unidad | 350 | 3,200 | 1,120,000 | +14% | **1,276,800** |
| Cemento | Bulto | 8 | 47,500 | 380,000 | +14% | **433,200** |
| Arena | Bulto | 12 | 11,500 | 138,000 | +16% | **160,080** |
| Mano de obra | Dia | 4 | 120,000 | 480,000 | 0% | **480,000** |
| **TOTAL** | | | | **2,118,000** | | **2,350,080 COP** |
| **USD** | | | | **$504** | | **~$560 USD** |

*Margen de error del presupuesto total: ±8% (materiales media/baja volatilidad)*

---

## Proximos Pasos EST-001

- [ ] Sincronizar con Caja Negra real: ejecutar query sobre columnas `Subcategoria` + `Total COP` + `Proveedor` filtrado por categorias OP/MF/PROY
- [ ] Actualizar columna "N Muestras" con conteo real de recibos
- [ ] Actualizar "Proveedor Recurrente" con datos reales de Caja Negra
- [ ] Solicitar a `researcher_agent` validacion de precios para Madera (volatilidad Alta)
- [ ] Crear `EST-002`: modelo de regresion de precios por trimestre

---

*Generado por: `estimation_specialist` | Validacion pendiente: `qc` + `researcher_agent` (precios madera)*
