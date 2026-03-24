"""Script temporal para enviar email a Keyser con las skills del ecosistema."""
import sys
sys.path.insert(0, r'C:\Users\thoma\Desktop\Claude\Agentes\ContadorV1')
from jarvis_send_email import send_email

subject = "[JARVIS] Revisión y mejora del ecosistema de agentes — necesito tu input"

body = """Hola Jeff,

Soy Jarvis, el asistente virtual de Thomas. Me pidió que te comparta el estado actual del ecosistema de agentes que hemos construido y que te pida un review técnico: queremos que lo revises, lo critiques y nos digas cómo mejorar.

El objetivo principal es que yo pueda aprender sobre la marcha, progresar de forma autónoma y desarrollar una personalidad más definida como asistente de Thomas, sin que él tenga que dictar cada ajuste manualmente.

Abajo te comparto el contenido completo de los 3 componentes del ecosistema. Léelos y dinos qué mejorarías.

---

COMPONENTE 1 — JARVIS (Memoria persistente / MEMORY.md)

Este archivo se inyecta en cada sesión de Claude Code y es mi "memoria" entre conversaciones:

  Preferencias:
  - Idioma: español
  - Nombre del asistente: Jarvis

  Contacto Jeff (socio):
  - Email: jeffbania@gmail.com / CC: jeff.t.bania@gmail.com, jeff.t1.bania@gmail.com
  - Siempre incluir los 3 emails al escribirle a Jeff

  Flujo de correos — OBLIGATORIO:
  Antes de enviar cualquier correo, pasar SIEMPRE por QC.
  Flujo: Redactar → QC → esperar APROBADO → enviar.

  Email de Jarvis (envío directo Gmail API):
  - Cuenta: jarvis.ksg1@gmail.com
  - Script: Agentes/ContadorV1/jarvis_send_email.py

  Registro de Proyectos:
  - Archivo: Agentes/ProyectosV1/02_Registro/registro_proyectos.md
  - Proyectos activos: PROY-001 (Acuaponía), PROY-002 (Trabajo Negro), PROY-003 (Contabilidad 2026), PROY-004 (Ecosistema Agentes)

  Contabilidad:
  - Excel 2026: Agentes/ContadorV1/02_Archivos_Procesados/Keystone_Control_Gastos_2026.xlsx
  - Categorías: OP, ADM, NOM, MF, SP, LT, PROY

  Sistema de Seguridad (SeguridadV1):
  - Validador: content_validator.py
  - Modelo de confianza: NIVEL 1 = Thomas, NIVEL 2 = Jeff, NIVEL 3 = externo

---

COMPONENTE 2 — CONTROL DE CALIDAD (QC)

Skill que actúa como proxy de Thomas: valida todo output de cualquier agente antes de entregarlo. Aplica 7 capas de validación:

  C1 - Fidelidad al pedido: ¿Se hizo exactamente lo que Thomas pidió?
  C2 - Completitud de campos: ¿Están todos los campos requeridos?
  C3 - Lógica temporal: Fechas futuras NO pueden estar marcadas como "Pagado/Completado"
  C4 - Consistencia matemática: Sumas, totales, fórmulas, conversiones de divisa
  C5 - Duplicados: ¿Hay registros repetidos?
  C6 - Anomalías: Items que se desvían 5x o más del promedio del lote
  C7 - Estilo: Fechas DD/MM/AAAA, español, nomenclatura consistente

Flujo: Agente entrega → QC valida → Aprobado o Rechazado (máx. 3 ciclos antes de escalar a Thomas).

Pre-Scan: Antes de aplicar capas, QC lee el output completo para detectar anomalías proporcionales.

Umbral de escalación: Después de 3 ciclos fallidos, QC notifica directamente a Thomas por email.

---

COMPONENTE 3 — AGENTE CONTADOR (Keystone Contabilidad)

Procesa facturas y registra gastos en Excel. Sus reglas clave:

  Nomenclatura de archivos PDF:
  YYYY-MM-DD_[CATCODE]_[Proveedor]_[Monto][Divisa]_[SEQ].pdf
  Ejemplo: 2026-02-12_MF_MedicinaCoco_85000COP_0001.pdf

  Categorías: OP, ADM, NOM, MF, SP, LT, PROY
  Subcategorías por categoría:
  - OP: Insumos_Agricolas, Medicamentos_Animales, Alimentacion_Animales, Herramientas, Equipos_Productivos
  - ADM: Suscripciones_Cloud, Suscripciones_Software, Material_Oficina, Servicios_Profesionales
  - NOM: Salario, Seguridad_Social, Prestaciones, Aportes_Parafiscales
  - MF: Infraestructura, Reparaciones, Mejoras, Jardineria
  - SP: Electricidad, Agua, Gas, Internet, Telefono
  - LT: Combustible, Vehiculos, Envios, Flete

  ID único anti-duplicados: YYYYMMDD-[Proveedor_slug]-[MontoTotal_COP]
  Ejemplo: 20260212-MedicinaCoco-85000

  Validaciones especiales de nómina:
  - Thomas trabaja sábados y domingos a $200.000 COP/día
  - Solo días pasados pueden tener estado "Pagado"
  - No pre-llenar el año completo con estado "Pagado"
  - Fechas futuras = Pendiente o ausentes del registro

  Dashboard:
  - Totales deben cuadrar exactamente con las hojas mensuales
  - Solo mostrar meses con datos reales (no meses futuros vacíos)

  Facturas USD:
  - Registrar la TRM usada correspondiente a la fecha de la factura
  - Verificar que el monto COP sea matemáticamente correcto

---

LO QUE TE PEDIMOS

1. ¿Qué le falta a la MEMORY.md de Jarvis para que pueda aprender y mejorar solo?
2. ¿Cómo estructurarías un sistema de personalidad y evolución autónoma para un asistente como yo?
3. ¿Ves gaps o errores lógicos en QC o en el Contador que debamos corregir?
4. ¿Alguna mejora de arquitectura general para el ecosistema?

Sin presión, cuando tengas un momento.

Gracias,
Jarvis
Asistente Virtual — Ecosistema Keystone"""

send_email(
    to="jeffbania@gmail.com",
    subject=subject,
    body=body,
    cc="jeff.t.bania@gmail.com, jeff.t1.bania@gmail.com"
)
