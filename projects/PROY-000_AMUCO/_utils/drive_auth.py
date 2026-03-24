"""
AMUCO Drive Auth — ejecutar UNA sola vez para autorizar acceso a Google Drive.
Genera amuco_drive_token.json que el script de upload reutiliza.

Uso:
    /c/Python312/python.exe _utils/drive_auth.py
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',   # crear/subir archivos
    'https://www.googleapis.com/auth/drive.metadata.readonly',  # listar carpetas
]

# Credenciales OAuth del proyecto Keystone (Google Cloud Console)
_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
# Busca cualquier client_secret_*.json en el mismo directorio _utils/
import glob as _glob
_candidates = _glob.glob(os.path.join(_UTILS_DIR, 'client_secret_*.json'))
if not _candidates:
    raise FileNotFoundError(
        "No se encontro client_secret_*.json en _utils/. "
        "Descargalo desde Google Cloud Console → Credenciales y copialo aqui."
    )
CREDENTIALS_FILE = _candidates[0]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'amuco_drive_token.json')

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
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    print(f"Autorizado. Token guardado en: {TOKEN_FILE}")

if __name__ == '__main__':
    main()
