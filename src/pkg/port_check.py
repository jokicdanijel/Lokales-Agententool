import socket
import sys

ALLOWED_PORTS = list(range(12344, 12400))
FORBIDDEN_PORTS = {8080}


def first_free_allowed_port():
    for port in ALLOWED_PORTS:
        if port in FORBIDDEN_PORTS:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                print(f"[OK] Verwende Port {port}")
                return port
            except OSError:
                continue
    print("[FEHLER] Kein freier erlaubter Port gefunden.")
    sys.exit(2)


if __name__ == "__main__":
    chosen = first_free_allowed_port()
    print(f"✅ Aktiver Port: {chosen}")
