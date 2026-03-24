"""
arrancar_whatsapp.py
====================
Un clic para dejar el chatbot de WhatsApp funcionando:

  1. Arranca el servidor Flask en puerto 5001
  2. Arranca ngrok y obtiene la URL pública
  3. Actualiza el webhook de Twilio automáticamente
  4. Muestra el estado final

Uso:
  /c/Python312/python.exe arrancar_whatsapp.py

Para detener todo: Ctrl+C
"""

import subprocess
import sys
import time
import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ── Credenciales Twilio (en .env) ─────────────────────────
TWILIO_ACCOUNT_SID    = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN     = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SANDBOX_NUMBER = os.getenv("TWILIO_SANDBOX_NUMBER", "whatsapp:+14155238886")

FLASK_PORT  = 5001
NGROK_API   = "http://localhost:4040/api/tunnels"
CHATBOT_DIR = os.path.join(os.path.dirname(__file__), "chatbot")

flask_proc = None
ngrok_proc = None


def check_port_free(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def kill_port(port: int):
    """Mata procesos en el puerto dado (Windows)."""
    result = subprocess.run(
        f'netstat -ano | findstr :{port}',
        shell=True, capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if parts and parts[-1].isdigit():
            pid = parts[-1]
            subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)


def start_flask():
    global flask_proc
    print("▶  Arrancando servidor Flask en puerto 5001...")
    if not check_port_free(FLASK_PORT):
        print(f"   Puerto {FLASK_PORT} ocupado — liberando...")
        kill_port(FLASK_PORT)
        time.sleep(1)

    flask_proc = subprocess.Popen(
        [sys.executable, "rag_chatbot.py"],
        cwd=CHATBOT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)

    # Verificar que arrancó
    try:
        r = requests.get(f"http://localhost:{FLASK_PORT}/", timeout=5)
        if r.status_code == 200:
            print(f"   ✓ Flask corriendo en http://localhost:{FLASK_PORT}")
            return True
    except Exception:
        pass

    print("   ✗ Flask no arrancó — revisa el código del chatbot")
    return False


def start_ngrok():
    global ngrok_proc
    print("▶  Arrancando ngrok...")

    # Matar ngrok anterior si existe
    subprocess.run("taskkill /F /IM ngrok.exe", shell=True, capture_output=True)
    time.sleep(1)

    ngrok_proc = subprocess.Popen(
        ["ngrok", "http", str(FLASK_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Esperar a que ngrok exponga la API local
    for i in range(10):
        time.sleep(1)
        try:
            r = requests.get(NGROK_API, timeout=3)
            tunnels = r.json().get("tunnels", [])
            for t in tunnels:
                if t.get("proto") == "https":
                    url = t["public_url"]
                    print(f"   ✓ ngrok activo: {url}")
                    return url
        except Exception:
            pass

    print("   ✗ ngrok no arrancó — asegúrate de que ngrok esté instalado y en el PATH")
    return None


def update_twilio_webhook(ngrok_url: str):
    """
    El Sandbox de Twilio no permite actualizar el webhook via API.
    Muestra las instrucciones con la URL lista para copiar (30 segundos).
    Con un número real de WhatsApp Business esto sería 100% automático.
    """
    webhook_url = f"{ngrok_url}/whatsapp"
    print(f"\n{'─'*55}")
    print(f"  TWILIO — Actualiza el webhook (30 seg):")
    print(f"{'─'*55}")
    print(f"  1. Abre: https://console.twilio.com/us1/develop/")
    print(f"           sms/try-it-out/whatsapp-learn")
    print(f"  2. Sección 'Sandbox Settings'")
    print(f"  3. Campo 'When a message comes in' → pega:")
    print()
    print(f"     {webhook_url}")
    print()
    print(f"  4. Guardar")
    print(f"{'─'*55}")


def main():
    print("=" * 55)
    print("  AMUCO WhatsApp — Arranque automático")
    print("=" * 55)

    # 1. Flask
    if not start_flask():
        sys.exit(1)

    # 2. ngrok
    ngrok_url = start_ngrok()
    if not ngrok_url:
        sys.exit(1)

    # 3. Twilio webhook
    update_twilio_webhook(ngrok_url)

    # 4. Resumen
    print("\n" + "=" * 55)
    print("  TODO LISTO")
    print("=" * 55)
    print(f"  Chatbot web:  http://localhost:{FLASK_PORT}")
    print(f"  WhatsApp:     {ngrok_url}/whatsapp")
    print(f"  Sandbox:      +1 415 523 8886")
    print(f"  Activar con:  join determine-begun")
    print()
    print("  Presiona Ctrl+C para detener todo")
    print("=" * 55)

    try:
        while True:
            time.sleep(5)
            # Verificar que Flask sigue vivo
            if flask_proc and flask_proc.poll() is not None:
                print("\n  ⚠  El servidor Flask se detuvo inesperadamente")
                break
    except KeyboardInterrupt:
        print("\n\n  Deteniendo servicios...")
    finally:
        if flask_proc:
            flask_proc.terminate()
            print("  ✓ Flask detenido")
        if ngrok_proc:
            ngrok_proc.terminate()
            subprocess.run("taskkill /F /IM ngrok.exe", shell=True, capture_output=True)
            print("  ✓ ngrok detenido")
        print("  Hasta luego.")


if __name__ == "__main__":
    main()
