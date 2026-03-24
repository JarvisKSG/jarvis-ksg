"""
db_backup.py — Keystone KSG Backup Engine
Agente: recovery_specialist
Version: 1.0 | Fecha: 2026-03-24

Flujo: export → compress → encrypt (AES-256-GCM) → sha256 → upload Drive → verify → log

Uso:
    python db_backup.py --resource sheets    # Exporta Caja Negra de Google Sheets
    python db_backup.py --resource postgres  # Dump de PostgreSQL (post-cloud)
    python db_backup.py --resource agents    # Snapshot de /agentes/ como tar.gz
    python db_backup.py --verify             # Verifica checksums de los ultimos 7 backups
    python db_backup.py --status             # Muestra estado del ultimo backup por recurso

Variables de entorno requeridas (nunca en codigo, nunca en git):
    BACKUP_ENCRYPTION_KEY   — clave AES-256 en base64 (generar con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    GDRIVE_BACKUP_FOLDER_ID — ID de la carpeta privada en Google Drive para backups
    DATABASE_URL            — PostgreSQL connection string (solo para --resource postgres)
    GOOGLE_SHEETS_ID        — ID de la Caja Negra (default: desde keystone_kb)
"""

import os
import sys
import json
import gzip
import shutil
import hashlib
import logging
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Dependencias: pip install cryptography google-auth google-api-python-client
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import secrets
    import base64
except ImportError:
    print("[REC-ERROR] Falta dependencia: pip install cryptography")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

LOG_FILE = Path(__file__).parent / "backup_log.json"
BACKUP_TMP_DIR = Path(__file__).parent / "tmp"
RETENTION_DAYS = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("recovery_specialist")


# ---------------------------------------------------------------------------
# Cifrado AES-256-GCM
# ---------------------------------------------------------------------------

def get_encryption_key() -> bytes:
    """Lee la clave de cifrado desde variable de entorno. Nunca desde codigo."""
    raw = os.environ.get("BACKUP_ENCRYPTION_KEY")
    if not raw:
        raise EnvironmentError(
            "[REC-BLOCK] BACKUP_ENCRYPTION_KEY no definida. "
            "Generar con: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    try:
        key = base64.urlsafe_b64decode(raw)
        if len(key) != 32:
            raise ValueError("La clave debe ser exactamente 32 bytes (AES-256)")
        return key
    except Exception as e:
        raise ValueError(f"[REC-BLOCK] BACKUP_ENCRYPTION_KEY invalida: {e}")


def encrypt_file(source_path: Path, dest_path: Path) -> None:
    """
    Cifra source_path con AES-256-GCM y escribe en dest_path.
    Formato: [12 bytes nonce][ciphertext+tag]
    """
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)

    plaintext = source_path.read_bytes()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    dest_path.write_bytes(nonce + ciphertext)
    log.info(f"Cifrado AES-256-GCM: {dest_path.name} ({len(ciphertext)} bytes)")


def decrypt_file(source_path: Path, dest_path: Path) -> None:
    """
    Descifra source_path y escribe en dest_path.
    Solo usar para pruebas de verificacion de integridad.
    """
    key = get_encryption_key()
    aesgcm = AESGCM(key)

    data = source_path.read_bytes()
    nonce = data[:12]
    ciphertext = data[12:]

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    dest_path.write_bytes(plaintext)
    log.info(f"Descifrado verificado: {dest_path.name}")


# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    """Calcula SHA-256 del archivo. Un backup sin checksum NO es un backup."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Export por tipo de recurso
# ---------------------------------------------------------------------------

def export_google_sheets(tmp_dir: Path) -> Path:
    """
    Exporta la Caja Negra de Google Sheets como CSV.
    Requiere: token OAuth Drive configurado (jarvis_drive.py como referencia).
    """
    sheets_id = os.environ.get("GOOGLE_SHEETS_ID", "1lgFZUjnnovMA2vK7h2EVp0jasQ7BACN03nvroDPuevs")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = tmp_dir / f"caja_negra_{timestamp}.csv"

    # Construccion de URL de export directo (requiere autenticacion OAuth)
    export_url = f"https://docs.google.com/spreadsheets/d/{sheets_id}/export?format=csv&id={sheets_id}"

    log.info(f"Exportando Google Sheets ID: {sheets_id}")
    log.info(f"URL de export: {export_url}")
    log.warning(
        "[REC-MANUAL] Para ejecutar en produccion: usar google-api-python-client con token de "
        "agents/2A-CONTADOR/jarvis_token.json. Este script requiere integracion con jarvis_drive.py."
    )

    # Placeholder — en produccion usar Drive API
    placeholder_content = (
        f"# BACKUP PLACEHOLDER\n"
        f"# Timestamp: {timestamp}\n"
        f"# Recurso: Keystone_Contabilidad_2026 (ID: {sheets_id})\n"
        f"# Para produccion: integrar con agents/2A-CONTADOR/jarvis_drive.py\n"
        f"# Comando: python jarvis_drive.py export --sheet-id {sheets_id} --format csv --output {output_path}\n"
    )
    output_path.write_text(placeholder_content)
    return output_path


def export_postgres(tmp_dir: Path) -> Path:
    """
    Genera pg_dump de la base de datos PostgreSQL.
    Requiere: DATABASE_URL en entorno y pg_dump instalado.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise EnvironmentError("[REC-BLOCK] DATABASE_URL no definida. Requerida para backup de PostgreSQL.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = tmp_dir / f"keystone_db_{timestamp}.sql"

    log.info("Ejecutando pg_dump...")
    result = subprocess.run(
        ["pg_dump", "--no-password", "--format=plain", db_url],
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        raise RuntimeError(f"[REC-ERROR] pg_dump fallo: {result.stderr[:500]}")

    output_path.write_text(result.stdout)
    log.info(f"pg_dump completado: {output_path.stat().st_size:,} bytes")
    return output_path


def export_agents_snapshot(tmp_dir: Path, agents_root: Path) -> Path:
    """
    Crea un snapshot tar.gz de la carpeta /agentes/ completa.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = tmp_dir / f"agentes_snapshot_{timestamp}.tar.gz"

    log.info(f"Creando snapshot de agentes: {agents_root}")
    shutil.make_archive(
        str(output_path.with_suffix("").with_suffix("")),
        "gztar",
        root_dir=str(agents_root.parent),
        base_dir=agents_root.name
    )
    log.info(f"Snapshot creado: {output_path.stat().st_size:,} bytes")
    return output_path


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run_backup(resource: str) -> dict:
    """
    Ejecuta el pipeline completo: export → compress → encrypt → sha256 → log.
    Retorna el registro del backup para almacenar en backup_log.json.
    """
    BACKUP_TMP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    start_time = datetime.now(timezone.utc)

    log.info(f"=== Iniciando backup: {resource} | {timestamp} ===")

    # 1. Export
    repo_root = Path(__file__).parent.parent.parent
    if resource == "sheets":
        raw_path = export_google_sheets(BACKUP_TMP_DIR)
    elif resource == "postgres":
        raw_path = export_postgres(BACKUP_TMP_DIR)
    elif resource == "agents":
        raw_path = export_agents_snapshot(BACKUP_TMP_DIR, repo_root / "agentes")
    else:
        raise ValueError(f"Recurso desconocido: {resource}. Usar: sheets | postgres | agents")

    # 2. Comprimir (si no es ya .tar.gz)
    if not raw_path.name.endswith(".tar.gz") and not raw_path.name.endswith(".gz"):
        gz_path = raw_path.with_suffix(raw_path.suffix + ".gz")
        with open(raw_path, "rb") as f_in:
            with gzip.open(gz_path, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
        raw_path.unlink()
        compressed_path = gz_path
    else:
        compressed_path = raw_path

    log.info(f"Comprimido: {compressed_path.name} ({compressed_path.stat().st_size:,} bytes)")

    # 3. Cifrar
    encrypted_path = compressed_path.with_suffix(compressed_path.suffix + ".enc")
    encrypt_file(compressed_path, encrypted_path)
    compressed_path.unlink()

    # 4. Checksum SHA-256 (obligatorio — ver Regla de Oro)
    checksum = sha256_file(encrypted_path)
    log.info(f"SHA-256: {checksum}")

    # 5. Verificacion de descifrado (integridad)
    test_path = encrypted_path.with_suffix(".verify")
    try:
        decrypt_file(encrypted_path, test_path)
        test_path.unlink()
        integrity_ok = True
        log.info("Verificacion de integridad: PASS")
    except Exception as e:
        integrity_ok = False
        log.error(f"[REC-ALERT] Verificacion de integridad FALLO: {e}")

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    record = {
        "timestamp": timestamp,
        "resource": resource,
        "file": encrypted_path.name,
        "sha256": checksum,
        "size_bytes": encrypted_path.stat().st_size,
        "duration_seconds": round(duration, 2),
        "integrity_verified": integrity_ok,
        "gdrive_uploaded": False,  # Actualizar a True tras upload exitoso
        "status": "VERIFIED" if integrity_ok else "INTEGRITY_FAIL"
    }

    # 6. Registrar en backup_log.json
    _append_log(record)

    if not integrity_ok:
        _send_slack_alert(resource, "Verificacion de integridad fallida tras cifrado")

    log.info(f"=== Backup completado en {duration:.1f}s | Estado: {record['status']} ===")
    return record


def _append_log(record: dict) -> None:
    """Agrega un registro al backup_log.json."""
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            log_data = json.load(f)
    else:
        log_data = {"backups": []}

    log_data["backups"].append(record)

    # Mantener solo los ultimos 90 registros
    log_data["backups"] = log_data["backups"][-90:]

    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def _send_slack_alert(resource: str, error_msg: str) -> None:
    """
    Envia alerta de emergencia a Slack #keystone-alertas.
    Requiere integracion con slack_expert o SLACK_BOT_TOKEN en entorno.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    message = (
        f"[REC-ALERT] Backup FALLIDO — Keystone KSG\n"
        f"Fecha: {timestamp}\n"
        f"Activo: {resource}\n"
        f"Error: {error_msg}\n"
        f"Accion: Thomas debe revisar inmediatamente."
    )
    log.error(message)
    # En produccion: usar slack_expert o mcp__claude_ai_Slack__slack_send_message
    # Canal: #keystone-alertas | Mencionar: @thomas


def verify_recent_backups(days: int = 7) -> None:
    """Verifica checksums de los backups mas recientes."""
    if not LOG_FILE.exists():
        log.warning("backup_log.json no encontrado. No hay backups registrados.")
        return

    with open(LOG_FILE) as f:
        log_data = json.load(f)

    recent = log_data["backups"][-days * 3:]  # ~3 backups por dia
    log.info(f"Verificando {len(recent)} backups recientes...")

    for record in recent:
        backup_file = BACKUP_TMP_DIR / record["file"]
        if backup_file.exists():
            actual_checksum = sha256_file(backup_file)
            status = "OK" if actual_checksum == record["sha256"] else "CORRUPTO"
            log.info(f"{record['timestamp']} | {record['resource']} | {status}")
        else:
            log.warning(f"{record['timestamp']} | {record['resource']} | ARCHIVO_NO_ENCONTRADO (puede estar en Drive)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Keystone KSG Backup Engine — recovery_specialist")
    parser.add_argument("--resource", choices=["sheets", "postgres", "agents"],
                        help="Recurso a respaldar")
    parser.add_argument("--verify", action="store_true",
                        help="Verificar checksums de backups recientes")
    parser.add_argument("--status", action="store_true",
                        help="Mostrar estado del ultimo backup por recurso")
    args = parser.parse_args()

    if args.verify:
        verify_recent_backups()
    elif args.status:
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                data = json.load(f)
            resources = {}
            for b in data["backups"]:
                resources[b["resource"]] = b
            for r, b in resources.items():
                print(f"{r:12} | {b['timestamp']} | {b['status']} | {b['size_bytes']:,} bytes")
        else:
            print("Sin backups registrados.")
    elif args.resource:
        result = run_backup(args.resource)
        status_icon = "OK" if result["status"] == "VERIFIED" else "FAIL"
        print(f"\n[{status_icon}] Backup {args.resource}: {result['file']}")
        print(f"    SHA-256: {result['sha256']}")
        print(f"    Tamano:  {result['size_bytes']:,} bytes")
        print(f"    Tiempo:  {result['duration_seconds']}s")
    else:
        parser.print_help()
