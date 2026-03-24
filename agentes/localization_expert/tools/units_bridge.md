# Units Bridge — Tabla de Conversion Oficial Keystone KSG
**Agente:** `localization_expert`
**Version:** 1.0 | **Fecha:** 2026-03-24
**Uso obligatorio:** Todo agente que genere medidas fisicas para el proyecto Deck / Finca Barbosa debe referenciar esta tabla. Aplica especialmente a: `architect_designer`, `civil_structural_engineer`, `fluids_hvac_engineer`, `estimation_specialist`.

---

> **Regla de uso:** Las especificaciones tecnicas internas de Keystone Colombia usan el **Sistema Internacional (SI)** como unidad primaria. Las comunicaciones a Jeff Bania incluyen **siempre** el equivalente en sistema imperial entre parentesis.
>
> Formato estandar: `45.5 m² (489.7 ft²)`

---

## Longitud

| Unidad Colombia (SI) | Equivalente USA (Imperial) | Factor | Ejemplo Deck |
|---------------------|---------------------------|--------|--------------|
| 1 metro (m) | 3.28084 pies (ft) | × 3.28084 | Largo deck: 8 m = 26.25 ft |
| 1 centimetro (cm) | 0.3937 pulgadas (in) | × 0.3937 | Espesor tabla: 4 cm = 1.57 in |
| 1 milimetro (mm) | 0.03937 pulgadas (in) | × 0.03937 | Tolerancia: 5 mm = 0.20 in |
| 1 pie (ft) | 0.3048 metros (m) | × 0.3048 | — |
| 1 pulgada (in) | 2.54 centimetros (cm) | × 2.54 | Tornillo 3/8 in = 0.95 cm |

**Conversiones rapidas para el Deck Finca Barbosa:**

| Medida tipica | SI (Colombia) | Imperial (USA / Jeff) |
|---------------|---------------|-----------------------|
| Ancho pasillo | 0.90 m | 2 ft 11 in |
| Altura barandal | 1.10 m | 3 ft 7 in |
| Separacion postes | 2.40 m | 7 ft 10 in |
| Largo modulo deck | 3.00 m | 9 ft 10 in |
| Ancho tabla deck | 0.14 m | 5.5 in |
| Espesor tabla | 0.038 m | 1.5 in |

---

## Area

| Unidad Colombia (SI) | Equivalente USA (Imperial) | Factor |
|---------------------|---------------------------|--------|
| 1 metro cuadrado (m²) | 10.7639 pies cuadrados (ft²) | × 10.7639 |
| 1 pie cuadrado (ft²) | 0.0929 metros cuadrados (m²) | × 0.0929 |
| 1 hectarea (ha) | 2.4711 acres | × 2.4711 |
| 1 acre | 0.4047 hectareas (ha) | × 0.4047 |

**Areas tipicas del Deck:**

| Zona | Area (m²) | Area (ft²) | Nota |
|------|-----------|------------|------|
| Deck principal | 24.0 m² | 258.3 ft² | Estimado |
| Zona de parrilla | 6.0 m² | 64.6 ft² | Estimado |
| Acceso/escalera | 4.5 m² | 48.4 ft² | Estimado |
| **TOTAL** | **34.5 m²** | **371.4 ft²** | Pendiente planos ARC-001 |

---

## Volumen

| Unidad Colombia (SI) | Equivalente USA (Imperial) | Factor |
|---------------------|---------------------------|--------|
| 1 litro (L) | 0.26417 galones (gal) | × 0.26417 |
| 1 galon (gal) | 3.78541 litros (L) | × 3.78541 |
| 1 metro cubico (m³) | 35.3147 pies cubicos (ft³) | × 35.3147 |
| 1 pie cubico (ft³) | 0.02832 metros cubicos (m³) | × 0.02832 |

---

## Masa y Carga

| Unidad Colombia (SI) | Equivalente USA (Imperial) | Factor |
|---------------------|---------------------------|--------|
| 1 kilogramo (kg) | 2.20462 libras (lb) | × 2.20462 |
| 1 libra (lb) | 0.45359 kilogramos (kg) | × 0.45359 |
| 1 tonelada (t) | 2,204.62 libras (lb) | × 2,204.62 |
| 1 kN/m² (kPa) | 20.885 lbf/ft² (psf) | × 20.885 |
| 1 kgf/cm² | 14.2233 psi | × 14.2233 |

**Cargas tipicas para calculo estructural del Deck (referencia civil_structural_engineer):**

| Tipo de carga | Valor SI | Valor Imperial |
|---------------|----------|----------------|
| Carga muerta deck (madera) | 0.5 kN/m² | 10.4 psf |
| Carga viva (uso residencial) | 2.0 kN/m² | 41.8 psf |
| Carga viva (uso reunion) | 4.8 kN/m² | 100.3 psf |
| Carga viento (zona Barbosa) | 0.8 kN/m² | 16.7 psf |

---

## Temperatura

| Celsius (°C) — Colombia | Fahrenheit (°F) — USA | Formula |
|------------------------|----------------------|---------|
| 0°C | 32°F | °F = (°C × 9/5) + 32 |
| 15°C (fresco Barbosa) | 59°F | — |
| 22°C (tipico dia) | 71.6°F | — |
| 30°C (caluroso) | 86°F | — |

---

## Materiales de Construccion — Equivalencias de Presentacion

| Material | Presentacion Colombia | Equivalente USA |
|----------|-----------------------|----------------|
| Cemento | Bulto 50 kg | ~110 lb bag |
| Varilla acero 3/8" | Longitud 6 m | 19 ft 8 in |
| Madera tabla | Pie lineal (pie = 30.48 cm) | Linear foot — identicos |
| Arena | Bulto 40 kg / m³ | 88 lb bag / 35.3 ft³ |
| Puntilla | Caja libra (453 g) | 1 lb box — identicos |

---

## Formula de Conversion Programatica (para agentes)

```python
# Constantes oficiales Keystone — NO modificar sin aprobacion localization_expert
CONVERSIONS = {
    # Longitud
    "m_to_ft": 3.28084,
    "ft_to_m": 0.30480,
    "cm_to_in": 0.39370,
    "in_to_cm": 2.54000,
    "mm_to_in": 0.03937,

    # Area
    "m2_to_ft2": 10.76391,
    "ft2_to_m2": 0.09290,

    # Volumen
    "L_to_gal": 0.26417,
    "gal_to_L": 3.78541,
    "m3_to_ft3": 35.31467,

    # Masa
    "kg_to_lb": 2.20462,
    "lb_to_kg": 0.45359,

    # Temperatura
    "c_to_f": lambda c: (c * 9/5) + 32,
    "f_to_c": lambda f: (f - 32) * 5/9,

    # Presion / Carga
    "kpa_to_psf": 20.88543,
    "kgfcm2_to_psi": 14.22334,
}

def convert(value: float, unit_from: str, unit_to: str = None) -> float:
    key = f"{unit_from}_to_{unit_to}" if unit_to else unit_from
    factor = CONVERSIONS.get(key)
    if callable(factor):
        return factor(value)
    if factor:
        return round(value * factor, 4)
    raise ValueError(f"Conversion no definida: {key}. Ver units_bridge.md")
```

---

*Mantenido por: `localization_expert` | Cambios requieren aprobacion de Thomas | Referencia: NIST Handbook 44, ISO 80000*
