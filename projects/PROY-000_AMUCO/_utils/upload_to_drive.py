"""
AMUCO Drive Upload — sube todas las fichas tecnicas a Google Drive.

Estructura que crea en Drive:
    AMUCO - Fichas Tecnicas/
        Polyvinyl Acetate PVAC/
            *.pdf, *.docx ...
        Adipic Acid/
            ...
        ...

Uso:
    /c/Python312/python.exe _utils/upload_to_drive.py

Requiere haber corrido drive_auth.py al menos una vez.
"""
import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
]

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'amuco_drive_token.json')
FICHAS_DIR = os.path.join(os.path.dirname(__file__), '..', 'chatbot', 'fichas_tecnicas')
ROOT_FOLDER_NAME = 'AMUCO - Fichas Tecnicas'

MIME_TYPES = {
    '.pdf':  'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc':  'application/msword',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)


def get_or_create_folder(service, name, parent_id=None):
    """Busca una carpeta por nombre (y parent). La crea si no existe."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']

    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        metadata['parents'] = [parent_id]

    folder = service.files().create(body=metadata, fields='id').execute()
    return folder['id']


def file_exists_in_folder(service, filename, folder_id):
    """Verifica si un archivo ya existe en la carpeta (evita duplicados)."""
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields='files(id)').execute()
    return len(results.get('files', [])) > 0


def upload_file(service, local_path, folder_id):
    filename = os.path.basename(local_path)
    ext = Path(local_path).suffix.lower()
    mime = MIME_TYPES.get(ext, 'application/octet-stream')

    if file_exists_in_folder(service, filename, folder_id):
        return 'skipped'

    metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime, resumable=True)
    service.files().create(body=metadata, media_body=media, fields='id').execute()
    return 'uploaded'


def main():
    if not os.path.exists(TOKEN_FILE):
        print("ERROR: No se encontro el token. Corre primero: /c/Python312/python.exe _utils/drive_auth.py")
        return

    if not os.path.exists(FICHAS_DIR):
        print(f"ERROR: No se encontro la carpeta de fichas: {FICHAS_DIR}")
        return

    print("Conectando a Google Drive...")
    service = get_service()

    print(f"Creando carpeta raiz: '{ROOT_FOLDER_NAME}'...")
    root_id = get_or_create_folder(service, ROOT_FOLDER_NAME)
    print(f"  Carpeta raiz ID: {root_id}")

    uploaded = 0
    skipped = 0
    errors = 0

    # Iterar subcarpetas de productos
    product_dirs = [d for d in os.scandir(FICHAS_DIR) if d.is_dir()]
    total_products = len(product_dirs)

    for i, product_dir in enumerate(sorted(product_dirs, key=lambda x: x.name), 1):
        product_name = product_dir.name
        print(f"\n[{i}/{total_products}] {product_name}")

        product_folder_id = get_or_create_folder(service, product_name, root_id)

        files = [f for f in os.scandir(product_dir.path)
                 if f.is_file() and Path(f.name).suffix.lower() in MIME_TYPES]

        for file_entry in files:
            try:
                result = upload_file(service, file_entry.path, product_folder_id)
                if result == 'uploaded':
                    print(f"  [OK] {file_entry.name}")
                    uploaded += 1
                else:
                    print(f"  [SKIP] {file_entry.name} (ya existe)")
                    skipped += 1
            except Exception as e:
                print(f"  [ERR] {file_entry.name}: {e}")
                errors += 1

    print()
    print("=" * 40)
    print(f"Subidos:   {uploaded}")
    print(f"Saltados:  {skipped} (ya existian)")
    print(f"Errores:   {errors}")
    print(f"Carpeta Drive: https://drive.google.com/drive/folders/{root_id}")


if __name__ == '__main__':
    main()
