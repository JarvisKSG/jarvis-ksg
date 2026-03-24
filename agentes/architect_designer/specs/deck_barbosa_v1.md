# ARC-001 — Deck Finca Barbosa v1: Criterios de Diseño Base
**Agente:** `architect_designer`
**Fecha:** 2026-03-24
**Auditoria unidades:** `localization_expert` — pendiente revision formal
**Validacion estructural:** `civil_structural_engineer` — PENDIENTE (CIV-001)
**Normativa aplicada:** NSR-10 (Titulos B y G), NTC 2500
**Estado:** Criterios de diseno base — NO construir hasta aprobacion de CIV-001

---

> **Advertencia:** Las secciones transversales de los elementos estructurales marcadas con [PENDIENTE ESTRUCTURAL] requieren validacion de `civil_structural_engineer` antes de usarse como especificacion de obra.

---

## 1. Programa del Proyecto

**Proyecto:** Deck exterior Finca Barbosa
**Ubicacion:** Barbosa, Antioquia, Colombia
**Propietario:** Jeff Bania / Keystone KSG
**Uso:** Zona de reunion y esparcimiento al aire libre
**Clasificacion de uso NSR-10:** Grupo de uso I (estructuras de ocupacion normal)

### Dimensiones del Deck

| Parametro | SI (Colombia) | Imperial (Jeff) |
|-----------|---------------|-----------------|
| Largo | 15.24 m | **50 ft** |
| Ancho | 3.66 m | **12 ft** |
| Area total | **55.74 m²** | **600 ft²** |
| Altura libre sobre terreno (est.) | 0.60 – 1.20 m | 2 – 4 ft |
| Altura barandal (NSR-10 H.3) | 1.07 m min. | 3 ft 6 in min. |

*Nota: La altura exacta sobre terreno requiere nivelacion topografica en campo (pendiente visita).*

---

## 2. Cargas de Diseño — NSR-10 Titulo B

### Carga Muerta (CM) — Peso propio estimado

| Elemento | Valor SI | Valor Imperial | Referencia |
|----------|----------|----------------|------------|
| Tablones de piso (madera 1.5") | 0.25 kN/m² | 5.2 psf | NTC 2500 densidad ~550 kg/m³ |
| Estructura secundaria (vigas) | 0.18 kN/m² | 3.8 psf | Estimado secciones 2×8 |
| Barandal + pasamanos | 0.07 kN/m² | 1.5 psf | Elemento perimetral |
| **Total CM** | **0.50 kN/m²** | **10.4 psf** | — |

### Carga Viva (CV) — NSR-10 Articulo B.4.2

| Condicion de uso | Valor SI | Valor Imperial | Criterio NSR-10 |
|-----------------|----------|----------------|-----------------|
| Uso residencial (base) | 2.00 kN/m² | 41.8 psf | Tabla B.4-1 balcones y terrazas |
| Uso reunion (critico) | **4.80 kN/m²** | **100.3 psf** | Tabla B.4-1 areas de reunion |
| **Diseno (caso critico)** | **4.80 kN/m²** | **100.3 psf** | Controla para el diseno |

> **Criterio adoptado:** Se diseña para uso de reunión (4.80 kN/m²) dado que el deck de una finca puede ser usado para eventos. Este criterio es conservador y no implica costo significativo adicional en una estructura de madera.

### Carga de Viento — NSR-10 Capitulo B.6

| Parametro | Valor |
|-----------|-------|
| Zona de viento | B (Barbosa, Antioquia — altitud ~1,300 msnm) |
| Velocidad de diseno | 110 km/h (30.6 m/s) |
| Presion de diseno | 0.80 kN/m² (16.7 psf) |
| Aplicacion | Barandales y elementos expuestos perimetrales |

### Carga Sismica — NSR-10 Titulo A
*Nota: Para estructuras de uso Grupo I con area < 100 m², la NSR-10 permite diseño simplificado. Confirmacion requerida por `civil_structural_engineer` en CIV-001.*

---

## 3. Sistema Estructural Propuesto

### Esquema en planta — Vista superior

```
        [LARGO: 15.24 m / 50 ft]
        ◄──────────────────────►

  ┌─────┬─────┬─────┬─────┬─────┐  ▲
  │     │     │     │     │     │  │
  │  V1 │  V2 │  V3 │  V4 │  V5 │  │ [ANCHO: 3.66 m / 12 ft]
  │     │     │     │     │     │  │
  └─────┴─────┴─────┴─────┴─────┘  ▼

  P•──────────•──────────•──────────•  ← Viga principal (beam) sobre postes (P)
  |  ~3.05 m  |  ~3.05 m |  ~3.05 m |  ← Modulos @ 10 ft c/c (pendiente CIV-001)
  P•          P•         P•          P•  ← Postes (6 total — 3 por fila longitudinal)

  ←──── Tablones de piso perpendiculares al largo ────→
```

### Elementos estructurales — Predimensionamiento

| Elemento | Funcion | Seccion propuesta | SI | Imperial | Estado |
|----------|---------|------------------|----|----------|--------|
| Tablones de piso | Piso caminable | 1.5" × 5.5" | 3.8 × 14 cm | 1½"×5½" | OK — comercial |
| Viga secundaria (joist) | Soporte tablones | 2" × 8" @ 40 cm c/c | 5 × 20 cm @ 40 cm | 2"×8" @ 16" oc | [PENDIENTE ESTRUCTURAL] |
| Viga principal (beam) | Soporte joists | 3 × (2" × 10") | 3 × (5 × 25 cm) | 3× 2"×10" | [PENDIENTE ESTRUCTURAL] |
| Poste | Soporte vertical | 4" × 4" o 6" × 6" | 10×10 o 15×15 cm | 4"×4" o 6"×6" | [PENDIENTE ESTRUCTURAL] |
| Barandal | Seguridad perimetral | 2" × 4" | 5 × 10 cm | 2"×4" | OK — altura 1.07 m min. |

*Secciones propuestas basadas en tablas de predimensionamiento NSR-10 Titulo G. REQUIEREN verificacion de `civil_structural_engineer` antes de compra de materiales.*

---

## 4. Materiales Recomendados — Medellin

### Opcion A — Economica: Pino Patula Tratado (CCA)

| Elemento | Especie | Seccion | Long. comercial | Precio est./pie | Proveedor tipo |
|----------|---------|---------|-----------------|----------------|----------------|
| Tablones piso | Pino Patula CCA | 1"×6" | 3 m o 4 m | $4,200 COP | Deposito Medellin |
| Vigas joist | Pino Patula CCA | 2"×8" | 4 m o 6 m | $8,400 COP | Deposito Medellin |
| Vigas beam | Pino Patula CCA | 2"×10" | 4 m o 6 m | $10,500 COP | Deposito Medellin |
| Postes | Pino Patula CCA | 4"×4" | 3 m | $12,600 COP | Deposito Medellin |

> **Nota tratamiento CCA:** El Cromato de Cobre Arsenicado (CCA) protege contra insectos y hongos. Para zonas al aire libre en clima humedo como Barbosa, el tratamiento es OBLIGATORIO. Exigir certificado de retencion minima 4 kg/m³ (uso exterior segun AWPA).

### Opcion B — Premium: Acacia Melanoxylon

| Ventaja | Desventaja |
|---------|-----------|
| Durabilidad natural 25-40 años sin tratamiento quimico | Costo ~55% mayor que pino tratado |
| Resistencia natural a insectos y hongos | Menor disponibilidad — requiere pedido anticipado |
| Mejor apariencia estetica — veta atractiva | — |

**Recomendacion `architect_designer`:** Opcion A (Pino tratado CCA) para presupuesto inicial. Si Jeff aprueba inversion premium, considerar Acacia para tablones de piso (superficie visible) y pino tratado para estructura no visible.

### Herrajes y Fijaciones (NSR-10 G.12)

| Elemento | Especificacion | Razon |
|----------|---------------|-------|
| Tornillos de piso | Inoxidable 316 o galvanizado G185 | Resistencia a corrosion exterior |
| Pernos estructurales | 1/2" galvanizado caliente | Conexiones beam-poste (NSR-10 G.12.3) |
| Anclas de poste | Simpson Strong-Tie PCZ o equivalente | Separar madera del concreto — evitar pudricion |
| Clavos framing | 16d galvanizado | Ensambles secundarios |

---

## 5. Estimado Preliminar de Cantidades

*(Requiere validacion de cantidades exactas tras aprobacion de CIV-001)*

| Partida | Unidad | Cantidad est. | Precio unit. COP | Total est. COP | Total est. USD |
|---------|--------|--------------|-----------------|----------------|----------------|
| Tablones piso 1"×6" | Pie lineal | 900 pl | $4,200 | $3,780,000 | ~$900 |
| Vigas joist 2"×8" | Pie lineal | 480 pl | $8,400 | $4,032,000 | ~$960 |
| Vigas beam 2"×10" | Pie lineal | 180 pl | $10,500 | $1,890,000 | ~$450 |
| Postes 4"×4" | Unidad | 8 un | $85,000 | $680,000 | ~$162 |
| Herrajes y fijaciones | Global | 1 | $850,000 | $850,000 | ~$202 |
| Concreto pedestales (6 un) | m³ | 0.5 | $450,000 | $225,000 | ~$54 |
| **TOTAL MATERIALES** | — | — | — | **$11,457,000** | **~$2,728** |
| Mano de obra (est.) | Jornal | 20 | $120,000 | $2,400,000 | ~$571 |
| **TOTAL OBRA** | — | — | — | **$13,857,000** | **~$3,299** |

*TRM referencia: $4,200 COP/USD (2026-03-24) | Margen de error: ±25% — prediseño sin ingenieria detallada*

---

## 6. Proximos Pasos

| Paso | Accion | Responsable | Bloquea |
|------|--------|-------------|---------|
| 1 | Validar secciones estructurales [PENDIENTE] | `civil_structural_engineer` (CIV-001) | Compra de materiales |
| 2 | Auditar conversiones m/ft y COP/USD | `localization_expert` | Envio a QC |
| 3 | Visita de campo: nivelacion terreno y puntos de apoyo | Thomas | Definicion postes |
| 4 | Validar presupuesto contra precios reales de depositos | `estimation_specialist` | Aprobacion de Jeff |
| 5 | Diseno de cimentacion (pedestales o dados de concreto) | `civil_structural_engineer` | Inicio de obra |

---

*Generado por: `architect_designer` | Auditoria pendiente: `localization_expert` + `civil_structural_engineer` | QC: pendiente aprobacion de pasos anteriores*
