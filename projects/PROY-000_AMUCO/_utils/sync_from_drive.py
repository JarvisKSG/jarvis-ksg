"""
AMUCO Drive Sync — descarga fichas tecnicas desde Google Drive y reconstruye ChromaDB.

Uso:
    # Sincronizar todo + re-indexar
    /c/Python312/python.exe _utils/sync_from_drive.py

    # Solo sincronizar archivos (sin re-indexar)
    /c/Python312/python.exe _utils/sync_from_drive.py --no-index

    # Solo re-indexar (sin descargar)
    /c/Python312/python.exe _utils/sync_from_drive.py --index-only

Requiere haber corrido drive_auth.py al menos una vez.
"""
import os
import sys
import hashlib
import subprocess
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
]

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'amuco_drive_token.json')
FICHAS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chatbot', 'fichas_tecnicas'))
ROOT_FOLDER_NAME = 'AMUCO - Fichas Tecnicas'
PYTHON = r'C:\Python312\python.exe'
RAG_INDEXER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chatbot', 'rag_indexer.py'))

ALLOWED_EXT = {'.pdf', '.docx', '.doc', '.xlsx'}


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)


def find_root_folder(service):
    query = f"name='{ROOT_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])
    if not files:
        print(f"ERROR: No se encontro la carpeta '{ROOT_FOLDER_NAME}' en Drive.")
        print("Asegurate de haber corrido upload_to_drive.py primero.")
        sys.exit(1)
    return files[0]['id']


def list_folder_contents(service, folder_id):
    """Lista subcarpetas y archivos de una carpeta."""
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields='files(id, name, mimeType, md5Checksum, size)',
        pageSize=1000
    ).execute()
    return results.get('files', [])


def download_file(service, file_id, dest_path):
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    with open(dest_path, 'wb') as f:
        f.write(buf.getvalue())


def md5_local(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def sync(service, root_id):
    downloaded = 0
    skipped = 0
    errors = 0

    os.makedirs(FICHAS_DIR, exist_ok=True)

    items = list_folder_contents(service, root_id)
    product_folders = [i for i in items if i['mimeType'] == 'application/vnd.google-apps.folder']

    print(f"Encontradas {len(product_folders)} carpetas de productos en Drive.")

    for folder in sorted(product_folders, key=lambda x: x['name']):
        product_name = folder['name']
        local_product_dir = os.path.join(FICHAS_DIR, product_name)
        os.makedirs(local_product_dir, exist_ok=True)

        files = [f for f in list_folder_contents(service, folder['id'])
                 if f['mimeType'] != 'application/vnd.google-apps.folder'
                 and Path(f['name']).suffix.lower() in ALLOWED_EXT]

        new_files = 0
        for f in files:
            dest = os.path.join(local_product_dir, f['name'])
            drive_md5 = f.get('md5Checksum', '')

            # Si existe localmente y el MD5 coincide, saltar
            if os.path.exists(dest) and drive_md5:
                if md5_local(dest) == drive_md5:
                    skipped += 1
                    continue

            try:
                download_file(service, f['id'], dest)
                new_files += 1
                downloaded += 1
            except Exception as e:
                print(f"  [ERR] {f['name']}: {e}")
                errors += 1

        if new_files > 0:
            print(f"  [{product_name}] {new_files} archivos nuevos/actualizados")

    print()
    print("=" * 40)
    print(f"Descargados/actualizados: {downloaded}")
    print(f"Sin cambios (saltados):   {skipped}")
    print(f"Errores:                  {errors}")
    return downloaded > 0


def run_indexer():
    print()
    print("Re-construyendo ChromaDB...")
    result = subprocess.run(
        [PYTHON, RAG_INDEXER],
        capture_output=False,
        text=True
    )
    if result.returncode == 0:
        print("ChromaDB reconstruido exitosamente.")
    else:
        print(f"ERROR al reconstruir ChromaDB (exit code {result.returncode}).")
        print("Corre manualmente: /c/Python312/python.exe chatbot/rag_indexer.py")


def main():
    index_only = '--index-only' in sys.argv
    no_index = '--no-index' in sys.argv

    if not os.path.exists(TOKEN_FILE):
        print("ERROR: Token no encontrado. Corre primero: /c/Python312/python.exe _utils/drive_auth.py")
        sys.exit(1)

    if not index_only:
        print("Conectando a Google Drive...")
        service = get_service()
        root_id = find_root_folder(service)
        print(f"Sincronizando desde Drive (carpeta ID: {root_id})...\n")
        hay_cambios = sync(service, root_id)
    else:
        hay_cambios = True

    if not no_index:
        if hay_cambios or index_only:
            run_indexer()
        else:
            print("\nNo hay cambios — ChromaDB no necesita actualizarse.")
    else:
        print("\nFlag --no-index: ChromaDB no se reconstruyo.")


if __name__ == '__main__':
    main()
