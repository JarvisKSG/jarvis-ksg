# Protocolo — Dominio Académico (Universidad)
**Activado cuando Thomas menciona "universidad", "clase" o "trabajo académico".**

<!-- CORE SECTION — READ ONLY -->

## Reglas del Dominio Académico

- **Workspace exclusivo:** `projects/universidad/` — no crear ni modificar archivos fuera de esta carpeta
- **Idioma:** español por defecto; inglés si el curso lo requiere explícitamente
- **Tono:** técnico-académico — claro, riguroso, sin lenguaje corporativo de Keystone
- **Universidad:** EAFIT — Ingeniería de Sistemas
- **Enfoque típico:** desarrollo de software, algoritmos, bases de datos, investigación, informes de clase

## Lo que NO aplica en este dominio

| Protocolo Keystone | Estado en modo académico |
|--------------------|--------------------------|
| TRM / conversión COP-USD | Suspendido |
| Categorías contables (OP, ADM, NOM…) | Suspendido |
| Pipeline QC corporativo (C1–C7) | Suspendido |
| Formato de reportes Keystone | Suspendido |
| Bilingual email rule | Suspendido |
| Kaiser / Jeff protocols | Suspendido |

> QC académico aplica solo si Thomas lo pide explícitamente para un trabajo de alta importancia.

## Flujo de Activación

```
Thomas menciona "universidad" / "clase" / "trabajo académico"
        ↓
Jarvis lee este archivo antes de actuar
        ↓
Toda la operación ocurre dentro de projects/universidad/
        ↓
Al terminar la tarea académica → retomar modo Keystone normal
```

## Estructura de Carpetas Recomendada

```
projects/universidad/
├── context.md              ← este archivo de contexto
├── [MATERIA_NOMBRE]/       ← una carpeta por materia
│   ├── context.md          ← descripción de la materia, profesor, fechas
│   └── [tarea o proyecto]
└── recursos/               ← material reutilizable entre materias
```

<!-- END OF CORE SECTION -->

---

<!-- EVOLUTION ZONE — Jarvis puede añadir reglas académicas aprendidas -->

## Evolution Zone

_Sin entradas — inicializado 2026-03-23._

<!-- [EVOLUTION ZONE END] -->
