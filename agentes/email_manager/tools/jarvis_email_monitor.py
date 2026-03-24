"""
Jarvis Email Monitor — Monitoreo permanente de correos
Revisa jarvis.ksg1@gmail.com cada 15 min y notifica a Thomas si hay correos importantes.
Registrado en Windows Task Scheduler para correr automáticamente.
"""
import os
import json
import base64
from datetime import datetime
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ===== CONFIG =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, 'jarvis_token.json')
SEEN_FILE = os.path.join(BASE_DIR, 'jarvis_emails_vistos.json')
LOG_FILE = os.path.join(BASE_DIR, 'jarvis_monitor_log.txt')

THOMAS_EMAIL = 'thomasreyesr@gmail.com'
JARVIS_EMAIL = 'jarvis.ksg1@gmail.com'

# Contactos prioritarios — notificar siempre
PRIORITY_SENDERS = [
    'jeffbania@gmail.com',
    'jeff.t.bania@gmail.com',
    'jeff.t1.bania@gmail.com',
]

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]

# ===== HELPERS =====
def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {msg}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen), f)

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_alert(service, subject, body):
    msg = MIMEText(body)
    msg['to'] = THOMAS_EMAIL
    msg['from'] = f'Jarvis <{JARVIS_EMAIL}>'
    msg['subject'] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    log(f'Alerta enviada a Thomas: {subject}')

def get_header(headers, name):
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ''

# ===== MAIN =====
def main():
    log('=== Jarvis Monitor iniciado ===')
    try:
        service = get_service()
        seen = load_seen()

        # Buscar emails no leidos
        result = service.users().messages().list(
            userId='me', q='is:unread', maxResults=20
        ).execute()
        messages = result.get('messages', [])

        if not messages:
            log('Sin correos nuevos.')
            return

        nuevos_importantes = []
        nuevos_otros = []

        for msg in messages:
            msg_id = msg['id']
            if msg_id in seen:
                continue

            # Leer detalles
            detail = service.users().messages().get(
                userId='me', messageId=msg_id, format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = detail['payload']['headers']
            sender = get_header(headers, 'From')
            subject = get_header(headers, 'Subject')
            date = get_header(headers, 'Date')

            seen.add(msg_id)
            log(f'Nuevo email: De={sender} | Asunto={subject}')

            # Clasificar por prioridad
            sender_lower = sender.lower()
            is_priority = any(p in sender_lower for p in PRIORITY_SENDERS)

            if is_priority:
                nuevos_importantes.append({'from': sender, 'subject': subject, 'date': date})
            else:
                nuevos_otros.append({'from': sender, 'subject': subject, 'date': date})

        save_seen(seen)

        # Notificar si hay emails importantes
        if nuevos_importantes:
            lines = [f'Jarvis detectó {len(nuevos_importantes)} correo(s) importante(s):\n']
            for e in nuevos_importantes:
                lines.append(f'  De:     {e["from"]}')
                lines.append(f'  Asunto: {e["subject"]}')
                lines.append(f'  Fecha:  {e["date"]}')
                lines.append('')
            if nuevos_otros:
                lines.append(f'Además hay {len(nuevos_otros)} correo(s) de otros remitentes.')
            lines.append('\n— Jarvis | jarvis.ksg1@gmail.com')
            body = '\n'.join(lines)
            send_alert(service, f'[Jarvis] {len(nuevos_importantes)} correo(s) nuevo(s) de Jeff', body)

        elif nuevos_otros:
            log(f'{len(nuevos_otros)} correo(s) nuevos de remitentes no prioritarios — sin alerta.')

    except Exception as e:
        log(f'ERROR: {e}')

if __name__ == '__main__':
    main()
