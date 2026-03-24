"""
Jarvis - Enviar email via Gmail API
Uso: python jarvis_send_email.py "to@email.com" "Asunto" "Cuerpo del mensaje" ["cc"] ["archivo1,archivo2"]
"""
import sys
import os
import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
]

BASE_DIR = os.path.dirname(__file__)
TOKEN_FILE = os.path.join(BASE_DIR, 'jarvis_token.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR,
    'client_secret_862191406250-suinugfdcbjl0ln2lioj66hmic0gssr4.apps.googleusercontent.com.json')


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def send_email(to, subject, body, cc=None, attachments=None):
    service = get_service()
    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body))
    else:
        msg = MIMEText(body)
    msg['to'] = to
    msg['subject'] = subject
    msg['from'] = 'Jarvis <jarvis.ksg1@gmail.com>'
    if cc:
        msg['cc'] = cc
    if attachments:
        for filepath in attachments:
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            main_type, sub_type = mime_type.split('/', 1)
            with open(filepath, 'rb') as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
            msg.attach(part)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    print('Enviado. Message ID: ' + result['id'])
    return result


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Uso: python jarvis_send_email.py "to" "asunto" "cuerpo" ["cc"] ["archivo1,archivo2"]')
        sys.exit(1)
    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    cc = sys.argv[4] if len(sys.argv) > 4 else None
    attachments = sys.argv[5].split(',') if len(sys.argv) > 5 else None
    send_email(to, subject, body, cc, attachments)
