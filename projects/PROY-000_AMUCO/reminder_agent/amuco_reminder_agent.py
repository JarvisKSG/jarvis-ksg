"""
PROY-005 — Agente de Recordatorios de Cotizacion AMUCO
======================================================
Detecta cotizaciones en estado 'quoted' con 2+ dias sin respuesta
y envia recordatorio de seguimiento al cliente.

MODO SEGURO: DRY_RUN = True por defecto.
Cambiar a False solo cuando Thomas apruebe.
"""

import requests
import re
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ─────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────
DRY_RUN = False         # False = envia emails (pero a TEST_EMAIL si TEST_MODE=True)
TEST_MODE = True        # True = redirige todos los emails a TEST_EMAIL (simulacion segura)
TEST_EMAIL = os.getenv("TEST_EMAIL", "thomasreyesr@gmail.com")

DAYS_THRESHOLD = 2      # dias sin respuesta antes de enviar recordatorio
COOLDOWN_DAYS  = 4      # dias de espera antes de volver a recordar la misma cotizacion
HAROLD_AGENT_ID = "129" # ID de Harold Santiago en kiwi.amucoinc.com
MAX_REMINDERS = 3       # limite de seguridad por ejecucion (3 para test)

# Log de recordatorios ya enviados (anti-duplicado)
SENT_LOG_PATH = Path(__file__).parent / "sent_log.json"

AMUCO_URL  = os.getenv("AMUCO_URL",  "https://kiwi.amucoinc.com")
AMUCO_USER = os.getenv("AMUCO_USER", "harold.santiago@amucoinc.com")
AMUCO_PASS = os.getenv("AMUCO_PASS")

# Email de Jarvis para envios
JARVIS_EMAIL = os.getenv("JARVIS_EMAIL", "jarvis.ksg1@gmail.com")
HAROLD_EMAIL = os.getenv("HAROLD_EMAIL", "harold.santiago@amucoinc.com")

# ─────────────────────────────────────────────
# TEMPLATES DE EMAIL (EN / ES / PT)
# ─────────────────────────────────────────────
# Templates basados en correos reales de Harold (analizados 2026-03-20)
# Tono: directo, personalizado, menciona condiciones del mercado como urgencia
EMAIL_TEMPLATES = {
    "en": {
        "subject": "Follow-up: Offer #{quote_id} — {company}",
        "body": """Dear {customer_name},

Hope you're doing well.

I wanted to follow up on the offer we shared on {quote_date} (Ref. #{quote_id}), totaling USD {total_sales}.

Given current market conditions, offer validity windows are quite short. I'd love to hear your thoughts — whether you're ready to move forward, need to adjust the terms, or if there's anything I can help clarify to make it easier to decide.

Looking forward to your response.

Best regards,
Harold Santiago
Sales | AMUCO INC.
WhatsApp: +57 300 842 1904

Best Regards / Saludos Cordiales"""
    },
    "es": {
        "subject": "Seguimiento oferta #{quote_id} — {company}",
        "body": """Estimado/a {customer_name},

Espero que se encuentre muy bien.

Queria dar seguimiento a la oferta que le compartimos el {quote_date} (Ref. #{quote_id}) por un total de USD {total_sales}.

Dadas las condiciones actuales del mercado, la validez de estas ofertas es bastante corta. Me gustaria conocer sus comentarios con el fin de poder avanzar, o revisar si requiere algun ajuste en precio, volumen o condiciones.

Quedo muy atento a su respuesta.

Saludos cordiales,
Harold Santiago
Comercial | AMUCO INC.
WhatsApp: +57 300 842 1904

Best Regards / Saludos Cordiales"""
    },
    "pt": {
        "subject": "Acompanhamento oferta #{quote_id} — {company}",
        "body": """Prezado/a {customer_name},

Espero que esteja muito bem.

Gostaria de dar seguimento a oferta que enviamos em {quote_date} (Ref. #{quote_id}), no valor de USD {total_sales}.

Considerando as condicoes atuais do mercado, os prazos de validade das ofertas sao bastante curtos. Ficaria muito grato pelos seus comentarios para que possamos avancar, ou revisar qualquer ajuste necessario.

Aguardo sua resposta.

Atenciosamente,
Harold Santiago
Comercial | AMUCO INC.
WhatsApp: +57 300 842 1904

Best Regards / Saludos Cordiales"""
    }
}


# ─────────────────────────────────────────────
# ANTI-DUPLICADO — sent_log.json
# ─────────────────────────────────────────────

def load_sent_log() -> dict:
    """Carga el log de recordatorios enviados."""
    if SENT_LOG_PATH.exists():
        with open(SENT_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_sent_log(log: dict):
    """Guarda el log actualizado."""
    with open(SENT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def already_reminded(quote_id: str, log: dict) -> bool:
    """Devuelve True si ya se envio recordatorio a esta cotizacion recientemente."""
    if str(quote_id) not in log:
        return False
    last_sent = datetime.fromisoformat(log[str(quote_id)])
    return (datetime.now() - last_sent).days < COOLDOWN_DAYS


def mark_as_reminded(quote_id: str, log: dict):
    """Registra que se envio recordatorio a esta cotizacion."""
    log[str(quote_id)] = datetime.now().isoformat()


def detect_language(company_name: str) -> str:
    """Detecta idioma basado en el nombre de la empresa/pais."""
    name_lower = company_name.lower()
    # Empresas tipicamente hispanohablantes
    spanish_indicators = ["s.a.", "s.a.s", "ltda", "s.r.l.", "quimica", "industrias",
                          "argentina", "colombia", "mexico", "chile", "peru"]
    # Empresas tipicamente lusohablantes
    portuguese_indicators = ["brasil", "brazil", "ltda", "industria e comercio",
                             "comercio ltda", "s/a"]
    for ind in portuguese_indicators:
        if ind in name_lower and ("brasil" in name_lower or "brazil" in name_lower or "comercio" in name_lower):
            return "pt"
    for ind in spanish_indicators:
        if ind in name_lower:
            return "es"
    return "en"


class AmucoSession:
    """Maneja la sesion autenticada con kiwi.amucoinc.com."""

    def __init__(self):
        self.session = requests.Session()
        self.csrf_name = None
        self.csrf_val = None
        self._logged_in = False

    def login(self) -> bool:
        try:
            r = self.session.get(f"{AMUCO_URL}/")
            csrf_match = re.search(r'name="(__[^"]+)"[^>]*value="([^"]+)"', r.text)
            if not csrf_match:
                print("[ERROR] No se encontro token CSRF en login")
                return False
            self.csrf_name = csrf_match.group(1)
            self.csrf_val = csrf_match.group(2)

            login_data = {
                "username": AMUCO_USER,
                "password": AMUCO_PASS,
                self.csrf_name: self.csrf_val
            }
            r2 = self.session.post(f"{AMUCO_URL}/", data=login_data, allow_redirects=True)
            if r2.status_code == 200:
                # Refrescar CSRF para requests siguientes
                r3 = self.session.get(f"{AMUCO_URL}/administrator/amuco_customer_request", allow_redirects=True)
                csrf2 = re.search(r"'(__[^']+)':\s*'([^']+)'", r3.text)
                if csrf2:
                    self.csrf_name = csrf2.group(1)
                    self.csrf_val = csrf2.group(2)
                self._logged_in = True
                print("[OK] Login exitoso en kiwi.amucoinc.com")
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Login fallido: {e}")
            return False

    def get_quoted_quotations(self, agent_id: str, limit: int = 500) -> list:
        """Obtiene todas las cotizaciones en estado quoted del agente."""
        if not self._logged_in:
            return []
        payload = {
            "draw": "1", "start": "0", "length": str(limit),
            "search[value]": "", "search[regex]": "false",
            "columns[0][data]": "id",
            "order[0][column]": "0", "order[0][dir]": "desc",
            "orden_columna": "id", "tipo_orden": "desc",
            self.csrf_name: self.csrf_val,
            "filters[status][]": "quoted",
            "filters[sales_agent][]": agent_id,
            "fromDate": "", "toDate": "", "customer": ""
        }
        try:
            r = self.session.post(
                f"{AMUCO_URL}/administrator/amuco_customer_request/get_data_table_quotation",
                data=payload,
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            d = r.json()
            return d.get("data", [])
        except Exception as e:
            print(f"[ERROR] No se pudo obtener cotizaciones: {e}")
            return []

    def get_customer_emails(self, customer_id: str) -> list:
        """Obtiene los emails de un cliente por su ID."""
        try:
            r = self.session.get(
                f"{AMUCO_URL}/administrator/amuco_customers/view/{customer_id}?popup=show",
                allow_redirects=True
            )
            emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)
            # Filtrar emails del sistema
            blacklist = ['amucoinc.com', 'jquery', 'example', 'font', 'cdnjs',
                         'bootstrap', 'google', 'cloudflare']
            clean = list(set([
                e for e in emails
                if not any(b in e.lower() for b in blacklist)
            ]))
            return clean
        except Exception as e:
            print(f"[ERROR] No se pudo obtener emails del cliente {customer_id}: {e}")
            return []


def parse_date(date_str: str) -> datetime | None:
    """Parsea fechas en formato DD-Mon-YYYY (ej: 18-Mar-2026)."""
    try:
        return datetime.strptime(date_str.strip(), "%d-%b-%Y")
    except:
        return None


def extract_customer_id(row: dict) -> str | None:
    """Extrae el customer_id del campo action (HTML)."""
    action_html = row.get("action", "")
    match = re.search(r'/amuco_customers/view/(\d+)', action_html)
    if match:
        return match.group(1)
    # Alternativa: del btn_id
    btn = row.get("btn_id", "")
    match2 = re.search(r'/edit/(\d+)', btn)
    return None


def send_email_via_jarvis(to: str, subject: str, body: str, cc: str = None) -> bool:
    """Envia email usando el script de Jarvis Gmail API."""
    script_path = os.path.join(
        os.path.dirname(__file__),
        "../../agents/2A-CONTADOR/jarvis_send_email.py"
    )
    script_path = os.path.normpath(script_path)

    if not os.path.exists(script_path):
        print(f"[ERROR] Script de email no encontrado: {script_path}")
        return False

    import subprocess
    cmd = ["python", script_path, to, subject, body]
    if cc:
        cmd.append(cc)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        return True
    else:
        print(f"[ERROR] Email fallido: {result.stderr[:200]}")
        return False


def run_reminder_agent():
    print("=" * 60)
    print("AMUCO Reminder Agent")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    modo = "DRY RUN (sin envios)" if DRY_RUN else (f"TEST MODE -> {TEST_EMAIL}" if TEST_MODE else "*** PRODUCCION — CLIENTES REALES ***")
    print(f"Modo: {modo}")
    print(f"Umbral: {DAYS_THRESHOLD} dias sin respuesta")
    print("=" * 60)

    amuco = AmucoSession()
    if not amuco.login():
        print("[ERROR] No se pudo iniciar sesion. Abortando.")
        sys.exit(1)

    print(f"\nObteniendo cotizaciones 'quoted' de Harold (ID: {HAROLD_AGENT_ID})...")
    quotations = amuco.get_quoted_quotations(HAROLD_AGENT_ID, limit=500)
    print(f"Total cotizaciones quoted encontradas: {len(quotations)}")

    cutoff_date = datetime.now() - timedelta(days=DAYS_THRESHOLD)
    to_remind = []

    for row in quotations:
        quote_date = parse_date(row.get("date", ""))
        if not quote_date:
            continue
        if quote_date <= cutoff_date:
            to_remind.append(row)

    print(f"Cotizaciones con {DAYS_THRESHOLD}+ dias sin respuesta: {len(to_remind)}")

    if not to_remind:
        print("\nNo hay cotizaciones que requieran seguimiento.")
        return []

    # ── Anti-duplicado: filtrar cotizaciones ya recordadas recientemente ──
    sent_log = load_sent_log()
    filtered = []
    for row in to_remind:
        qid = row.get("id", "?")
        if already_reminded(qid, sent_log):
            print(f"  [SKIP-DUP] #{qid} {row.get('amuco_customers_name','')[:30]} — recordatorio enviado hace menos de {COOLDOWN_DAYS} días")
        else:
            filtered.append(row)
    to_remind = filtered

    if not to_remind:
        print("\nTodas las cotizaciones pendientes ya recibieron recordatorio recientemente.")
        return []

    # ── Agrupar por cliente: un email por cliente aunque tenga varias ofertas ──
    by_customer: dict = {}
    for row in to_remind:
        btn_match = re.search(r'edit/(\d+)', row.get("btn_id", ""))
        quote_internal_id = btn_match.group(1) if btn_match else row.get("id", "?")
        try:
            r_edit = amuco.session.get(
                f"{AMUCO_URL}/administrator/amuco_customer_request/edit/{quote_internal_id}",
                allow_redirects=True, timeout=10
            )
            cust_id_match = re.search(r'amuco_customers/view/(\d+)', r_edit.text)
            customer_id = cust_id_match.group(1) if cust_id_match else None
        except:
            customer_id = None

        if not customer_id:
            print(f"  [SKIP] #{row.get('id','?')} {row.get('amuco_customers_name','')[:30]} — no se encontro customer_id")
            continue

        if customer_id not in by_customer:
            by_customer[customer_id] = {"rows": [], "emails": None}
        by_customer[customer_id]["rows"].append(row)

    # Limitar por seguridad (por cliente, no por cotizacion)
    customer_ids = list(by_customer.keys())[:MAX_REMINDERS]

    print(f"\nClientes a contactar: {len(customer_ids)} (max {MAX_REMINDERS})")
    print("-" * 60)

    sent_count = 0
    skipped_count = 0
    results = []

    for customer_id in customer_ids:
        group = by_customer[customer_id]
        rows = group["rows"]
        company = rows[0].get("amuco_customers_name", "Unknown")

        emails = amuco.get_customer_emails(customer_id)
        if not emails:
            print(f"  [SKIP] {company[:30]} — sin emails en el perfil")
            skipped_count += 1
            continue

        lang = detect_language(company)
        template = EMAIL_TEMPLATES[lang]

        # Si hay varias ofertas del mismo cliente → email consolidado
        if len(rows) > 1:
            quotes_detail = "\n".join(
                f"  • Ref. #{r.get('id','?')} | {r.get('date','')} | USD {r.get('total_sales','?')}"
                for r in rows
            )
            quote_ids = [r.get("id", "?") for r in rows]
            subject = template["subject"].format(quote_id=f"{quote_ids[0]}+{len(rows)-1}más", company=company)
            body = template["body"].format(
                customer_name=company,
                quote_date=rows[0].get("date", ""),
                quote_id=quote_ids[0],
                total_sales=rows[0].get("total_sales", "?")
            )
            body += f"\n\n(También tenemos pendientes las ofertas:\n{quotes_detail}\n)"
        else:
            row = rows[0]
            quote_id    = row.get("id", "?")
            total        = row.get("total_sales", "0")
            quote_date_str = row.get("date", "")
            quote_ids    = [quote_id]
            subject = template["subject"].format(quote_id=quote_id, company=company)
            body    = template["body"].format(
                customer_name=company,
                quote_date=quote_date_str,
                quote_id=quote_id,
                total_sales=total
            )

        real_emails   = emails
        primary_email = TEST_EMAIL if TEST_MODE else emails[0]
        cc_emails     = [] if TEST_MODE else (emails[1:3] if len(emails) > 1 else [])
        quote_ids_str = ", ".join(f"#{q}" for q in quote_ids)

        if TEST_MODE:
            subject = f"[TEST - Real: {real_emails[0]}] {subject}"
            body    = f"[SIMULACION — habria ido a: {', '.join(real_emails[:3])}]\n\n{body}"

        print(f"\n  Cliente: {company}")
        print(f"  Ofertas: {quote_ids_str}")
        print(f"  Emails reales: {real_emails[:3]}")
        print(f"  Idioma: {lang.upper()} | Enviando a: {primary_email} {'(TEST MODE)' if TEST_MODE else ''}")

        if DRY_RUN:
            print(f"  [DRY RUN] Email NO enviado")
            for qid in quote_ids:
                results.append({"id": qid, "company": company, "emails": real_emails, "lang": lang, "status": "dry_run"})
        else:
            cc = ", ".join(cc_emails) if cc_emails else None
            success = send_email_via_jarvis(primary_email, subject, body, cc)
            if success:
                print(f"  [OK] Email enviado a {primary_email}")
                sent_count += 1
                # Marcar TODAS las cotizaciones del cliente como recordadas
                for qid in quote_ids:
                    mark_as_reminded(qid, sent_log)
                save_sent_log(sent_log)

                for qid in quote_ids:
                    results.append({"id": qid, "company": company, "emails": real_emails,
                                    "lang": lang, "status": "sent_test" if TEST_MODE else "sent"})

                # Notificar a Harold
                notif_subject = f"Recordatorio enviado — {company} ({quote_ids_str})"
                notif_body = f"""Hola Harold,

Se envio automaticamente un recordatorio de seguimiento al cliente:

  Cliente:   {company}
  Ofertas:   {quote_ids_str}
  Emails:    {', '.join(real_emails[:3])}
  Idioma:    {lang.upper()}

{"[SIMULACION — email fue a " + TEST_EMAIL + ", no al cliente real]" if TEST_MODE else "El correo fue enviado directamente al cliente."}

---
Este es un mensaje automatico del sistema Jarvis / AMUCO Reminder Agent."""
                harold_notif = send_email_via_jarvis(HAROLD_EMAIL, notif_subject, notif_body)
                print(f"  [{'OK' if harold_notif else 'WARN'}] Notificacion a Harold")
            else:
                print(f"  [ERROR] Fallo el envio a {primary_email}")
                skipped_count += 1
                for qid in quote_ids:
                    results.append({"id": qid, "company": company, "emails": real_emails, "lang": lang, "status": "error"})

    print("\n" + "=" * 60)
    print("RESUMEN")
    print(f"  Cotizaciones analizadas: {len(to_remind)}")
    if DRY_RUN:
        print(f"  Habrian enviado recordatorio: {len(results)}")
        print(f"  Omitidas (sin email): {skipped_count}")
        print(f"\n  ** DRY RUN completado — cambia DRY_RUN = False para envios reales **")
    else:
        print(f"  Enviados: {sent_count}")
        print(f"  Omitidos/Error: {skipped_count}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    if "--send" in sys.argv:
        confirm = input("ATENCION: Modo envio real activado. Escribi 'CONFIRMAR' para continuar: ")
        if confirm.strip() == "CONFIRMAR":
            DRY_RUN = False
        else:
            print("Cancelado.")
            sys.exit(0)
    run_reminder_agent()
