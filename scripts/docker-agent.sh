#!/usr/bin/env bash
set -euo pipefail

# ===== Konfig-Defaults =====
DEFAULT_CONT_PORT=8080
DEFAULT_HOST_PORT=3000
PORT_STEPS=(3000 3100 3200 3300 3400 3500)

# Farbhelpers
ok(){ echo -e "\e[32m✓ $*\e[0m"; }
warn(){ echo -e "\e[33m! $*\e[0m"; }
err(){ echo -e "\e[31m✗ $*\e[0m" >&2; }

need() { command -v "$1" >/dev/null 2>&1 || { err "Befehl '$1' fehlt"; exit 127; }; }

# Freien Host-Port finden (aus Liste)
find_free_port() {
  for p in "${PORT_STEPS[@]}"; do
    if ! ss -lnt "sport = :$p" | grep -q ":$p"; then
      echo "$p"; return 0
    fi
  done
  err "Kein freier Port in ${PORT_STEPS[*]}"; return 1
}

# ===== Unterbefehle =====
cmd_help() {
  cat <<'HLP'
docker-agent.sh <cmd> [args]

Preflight/Repair:
  doctor                   - Diagnose: Docker/Compose, Versionen, Gruppenrechte, Sockel
  fix-perms                - 'docker' Gruppe + newgrp, Socket-Rechte prüfen
  uninstall-podman-docker  - entfernt Podman-Docker-Wrapper (verhindert Emulation)
  install-docker           - Docker CE + Compose v2 (Ubuntu/Debian), systemd enable
  rootless-enable          - Rootless Docker vorbereiten (NVIDIA beachten!)
  proxy-setup <host:port>  - Proxy für Docker/apt (Linux) konfigurieren (+Verify)
  ca-install <pemfile>     - Interne CA ins Docker trust.d importieren

Netz/Ports:
  port-free [PORT]         - prüft Port; ohne PORT wird freie Standardstaffel gesucht
  host-dns                 - prüft DNS, host.docker.internal Workaround auf Linux

Volumes/Storage:
  volume-ensure <name>     - legt Named Volume an (idempotent)
  bind-prepare <path>      - legt Host-Ordner an, setzt sinnvolle Rechte

Registries:
  login <registry> <user>  - docker login (Token/Passwort wird abgefragt)

GPU:
  nvidia-check             - prüft nvidia-smi & Toolkit, listet Runtimes

Run (Einzel/Compose):
  run-simple <image> [host_port] [cont_port]   - Einmalcontainer mit Port-Mapping
  compose-up [file]         - docker compose up -d (default: ./docker-compose.yml)
  compose-down [file]       - docker compose down
  compose-logs [name]       - docker logs -f <name>

Backup/Migration:
  volume-backup <name> <tarfile>   - sichert Volume
  volume-restore <name> <tarfile>  - stellt Volume wieder her

Cleanup (sicher):
  prune-dangling            - entfernt nur dangling images/networks/volumes
  prune-aggressive          - entfernt ungenutzte Ressourcen (mit Rückfrage)

Debug:
  sh <container>            - interaktive Shell im Container
  inspect <obj>             - docker inspect (Container/Image/Volume/Netz)
  ps                        - docker ps --format kompakt

HLP
}

cmd_doctor() {
  echo "== Versionen =="
  if command -v docker >/dev/null 2>&1; then
    docker --version || true
    docker compose version || true
  else
    warn "docker CLI nicht gefunden"
  fi
  echo "== Gruppen & Sockel =="
  id -nG || true
  ls -l /var/run/docker.sock 2>/dev/null || warn "/var/run/docker.sock fehlt"
  echo "== Dienst =="
  if command -v systemctl >/dev/null 2>&1; then
    systemctl is-active --quiet docker && ok "docker.service aktiv" || warn "docker.service nicht aktiv"
  fi
  echo "== Podman-Wrapper =="
  if command -v podman >/dev/null 2>&1 && command -v docker >/dev/null 2>&1; then
    docker --version 2>&1 | grep -qi "Emulate Docker CLI using podman" && warn "podman-docker aktiv/konflikt" || ok "kein podman-wrapper aktiv"
  fi
}

cmd_fix_perms() {
  need id
  if ! id -nG | tr ' ' '\n' | grep -qx docker; then
    if command -v sudo >/dev/null 2>&1; then
      sudo groupadd -f docker
      sudo usermod -aG docker "$USER"
      ok "User $USER zur Gruppe docker hinzugefügt"
      echo "Hinweis: neue Shell oder 'newgrp docker' nötig."
    else
      err "sudo fehlt, manuelles Hinzufügen nötig"; exit 1
    fi
  else
    ok "User $USER ist in Gruppe docker"
  fi
  if [ -S /var/run/docker.sock ]; then
    ls -l /var/run/docker.sock
    ok "Sockel vorhanden"
  else
    warn "Sockel fehlt (Dienst nicht aktiv?)"
  fi
}

cmd_uninstall_podman_docker() {
  if command -v sudo >/dev/null 2>&1; then
    sudo apt -y purge podman-docker python3-compose docker-compose || true
    ok "podman-docker entfernt (falls vorhanden)"
  else
    err "sudo fehlt"; exit 1
  fi
}

cmd_install_docker() {
  need curl
  if command -v sudo >/dev/null 2>&1; then
    . /etc/os-release
    case "${ID_LIKE:-$ID}" in
      *debian*|*ubuntu*)
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc >/dev/null
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" \
          | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        sudo systemctl enable --now docker
        sudo groupadd -f docker
        sudo usermod -aG docker "$USER"
        ok "Docker + Compose v2 installiert. -> 'newgrp docker' oder neue Session"
        ;;
      *)
        err "Auto-Install nur für Debian/Ubuntu implementiert"; exit 1;;
    esac
  else
    err "sudo fehlt"; exit 1
  fi
}

cmd_rootless_enable() {
  need dockerd-rootless-setuptool.sh || true
  if command -v dockerd-rootless-setuptool.sh >/dev/null 2>&1; then
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
    dockerd-rootless-setuptool.sh install
    ok "Rootless Docker eingerichtet (achte auf NVIDIA-Beschränkungen)"
  else
    err "dockerd-rootless-setuptool.sh nicht gefunden (docker-ce-rootless-extras?)"; exit 1
  fi
}

cmd_proxy_setup() {
  local proxy="${1:-}"
  [ -z "$proxy" ] && { err "proxy-setup <host:port>"; exit 2; }
  need sudo
  sudo mkdir -p /etc/systemd/system/docker.service.d
  cat <<EOF | sudo tee /etc/systemd/system/docker.service.d/proxy.conf >/dev/null
[Service]
Environment="HTTP_PROXY=http://$proxy" "HTTPS_PROXY=http://$proxy" "NO_PROXY=localhost,127.0.0.1"
EOF
  sudo systemctl daemon-reload
  sudo systemctl restart docker
  ok "Proxy gesetzt & Dienst neu gestartet"
}

cmd_ca_install() {
  local pem="${1:-}"
  [ -f "$pem" ] || { err "PEM nicht gefunden: $pem"; exit 2; }
  need sudo
  sudo mkdir -p /etc/docker/certs.d/ca-trust
  sudo cp "$pem" /etc/docker/certs.d/ca-trust/ca.crt
  sudo systemctl restart docker
  ok "CA installiert"
}

cmd_port_free() {
  local p="${1:-}"
  if [ -z "$p" ]; then
    p=$(find_free_port) || exit 1
    echo "$p"
  else
    if ss -lnt "sport = :$p" | grep -q ":$p"; then
      err "Port $p belegt"; exit 3
    else
      ok "Port $p ist frei"
    fi
  fi
}

cmd_host_dns() {
  echo "host.docker.internal -> Linux Workaround:"
  echo "docker run --rm --add-host=host.docker.internal:host-gateway alpine getent hosts host.docker.internal"
  docker run --rm --add-host=host.docker.internal:host-gateway alpine getent hosts host.docker.internal || true
}

cmd_volume_ensure() {
  local name="${1:?volume name fehlt}"
  docker volume inspect "$name" >/dev/null 2>&1 || docker volume create "$name" >/dev/null
  ok "Volume $name bereit"
}

cmd_bind_prepare() {
  local path="${1:?host path fehlt}"
  mkdir -p "$path"
  chmod 775 "$path" || true
  ok "Bind-Pfad $path vorbereitet"
}

cmd_login() {
  local reg="${1:?registry fehlt}" user="${2:?user fehlt}"
  docker login "$reg" -u "$user"
}

cmd_nvidia_check() {
  if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi || true; else warn "nvidia-smi nicht gefunden"; fi
  if docker info --format '{{json .Runtimes}}' | grep -q nvidia; then ok "NVIDIA Runtime verfügbar"; else warn "NVIDIA Runtime fehlt"; fi
}

cmd_run_simple() {
  local image="${1:?image fehlt}"
  local hport="${2:-$(find_free_port)}"
  local cport="${3:-$DEFAULT_CONT_PORT}"
  docker pull "$image"
  docker run -d --name "one-$(echo "$image" | tr '/:@' '_')" -p "$hport:$cport" "$image"
  ok "läuft auf http://localhost:$hport -> $image"
}

cmd_compose_up() {
  local file="${1:-docker-compose.yml}"
  [ -f "$file" ] || { err "Datei nicht gefunden: $file"; exit 2; }
  docker compose -f "$file" up -d
  ok "compose up -d"
}

cmd_compose_down() {
  local file="${1:-docker-compose.yml}"
  [ -f "$file" ] || { err "Datei nicht gefunden: $file"; exit 2; }
  docker compose -f "$file" down
  ok "compose down"
}

cmd_compose_logs() {
  local name="${1:?container name fehlt}"
  docker logs -f "$name"
}

cmd_volume_backup() {
  local name="${1:?volume name fehlt}" tarf="${2:?tarfile fehlend}"
  docker run --rm -v "$name":/v -v "$(pwd)":/out alpine sh -lc "cd /v && tar -czf /out/$tarf ."
  ok "Volume $name -> $tarf"
}

cmd_volume_restore() {
  local name="${1:?volume name fehlt}" tarf="${2:?tarfile fehlend}"
  docker run --rm -v "$name":/v -v "$(pwd)":/in alpine sh -lc "cd /v && tar -xzf /in/$tarf"
  ok "Tar $tarf -> Volume $name"
}

cmd_prune_dangling() {
  docker image prune -f
  docker volume prune -f
  docker network prune -f
  ok "dangling Ressourcen gepruned"
}

cmd_prune_aggressive() {
  read -r -p "Alle ungenutzten Ressourcen entfernen? [yes/N] " a
  [[ "$a" == "yes" ]] || { warn "abgebrochen"; exit 0; }
  docker system prune -a --volumes -f
  ok "Aggressive Bereinigung erledigt"
}

cmd_sh() { docker exec -it "${1:?container fehlt}" sh; }
cmd_inspect() { docker inspect "${1:?objekt fehlt}" | sed -n '1,120p'; }
cmd_ps(){ docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'; }

# ===== Router =====
case "${1:-help}" in
  help) cmd_help ;;
  doctor) cmd_doctor ;;
  fix-perms) cmd_fix_perms ;;
  uninstall-podman-docker) cmd_uninstall_podman_docker ;;
  install-docker) cmd_install_docker ;;
  rootless-enable) cmd_rootless_enable ;;
  proxy-setup) shift; cmd_proxy_setup "${1:-}";;
  ca-install) shift; cmd_ca_install "${1:-}";;
  port-free) shift; cmd_port_free "${1:-}";;
  host-dns) cmd_host_dns ;;
  volume-ensure) shift; cmd_volume_ensure "${1:-}";;
  bind-prepare) shift; cmd_bind_prepare "${1:-}";;
  login) shift; cmd_login "${1:-}" "${2:-}";;
  nvidia-check) cmd_nvidia_check ;;
  run-simple) shift; cmd_run_simple "${1:-}" "${2:-}" "${3:-}";;
  compose-up) shift; cmd_compose_up "${1:-}";;
  compose-down) shift; cmd_compose_down "${1:-}";;
  compose-logs) shift; cmd_compose_logs "${1:-}";;
  volume-backup) shift; cmd_volume_backup "${1:-}" "${2:-}";;
  volume-restore) shift; cmd_volume_restore "${1:-}" "${2:-}";;
  prune-dangling) cmd_prune_dangling ;;
  prune-aggressive) cmd_prune_aggressive ;;
  sh) shift; cmd_sh "${1:-}";;
  inspect) shift; cmd_inspect "${1:-}";;
  ps) cmd_ps ;;
  *)
    err "Unbekannter Befehl: ${1:-}"; cmd_help; exit 2 ;;
esac

