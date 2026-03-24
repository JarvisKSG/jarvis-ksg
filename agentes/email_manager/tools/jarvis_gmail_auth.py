"""
Jarvis Gmail Auth - Ejecutar UNA sola vez para autorizar.
Genera token.json que Jarvis usa para enviar correos.
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__),
    'client_secret_862191406250-suinugfdcbjl0ln2lioj66hmic0gssr4.apps.googleusercontent.com.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'jarvis_token.json')

def main():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    print("Autorizacion completada. Token guardado en jarvis_token.json")

if __name__ == '__main__':
    main()
