#!/bin/bash

# LocalAgent-Pro Installation Script
# Dieses Skript installiert benötigte Pakete und richtet die Sandbox ein.

set -e

echo "[LocalAgent-Pro] Installation gestartet..."

# Aktualisieren der Paketliste
if command -v apt >/dev/null 2>&1; then
  sudo apt update
  sudo apt install -y python3 python3-pip
fi

# Sandbox-Verzeichnis erstellen
SANDBOX_DIR="$HOME/localagent_sandbox"
if [ ! -d "$SANDBOX_DIR" ]; then
  mkdir -p "$SANDBOX_DIR"
  echo "[LocalAgent-Pro] Sandbox-Verzeichnis erstellt: $SANDBOX_DIR"
else
  echo "[LocalAgent-Pro] Sandbox-Verzeichnis existiert bereits: $SANDBOX_DIR"
fi

echo "[LocalAgent-Pro] Installation abgeschlossen."