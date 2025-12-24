# Agent Fleet Inventory Report

**Generated:** 2025-12-24 10:07:18 UTC

**Total Services:** 27

---

## opena20-dashboard

- **Image:** `opena20-dashboard:local`
- **Container:** `opena20-dashboard`
- **Compose File:** `docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Health Check:** ['CMD-SHELL', 'curl -f http://localhost:12349/health || exit 1']

---

## prometheus

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus-elion`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost:9090/-/healthy']

---

## grafana

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana-elion`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3001` → `3000` (tcp)
- **Networks:** elion
- **Dependencies:** prometheus
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:3000/api/health']

---

## portier

- **Image:** `unknown`
- **Container:** `portier`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12344/health']

---

## archivator

- **Image:** `unknown`
- **Container:** `archivator`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12345/health']

---

## telegram

- **Image:** `unknown`
- **Container:** `telegram`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12346` → `12346` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12346/health']

---

## inference

- **Image:** `unknown`
- **Container:** `inference`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12348` → `12348` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12348/health']

---

## browser

- **Image:** `unknown`
- **Container:** `browser`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** elion

---

## vscode

- **Image:** `unknown`
- **Container:** `vscode`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12350` → `12350` (tcp)
- **Networks:** elion

---

## email

- **Image:** `unknown`
- **Container:** `email`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** elion

---

## whatsapp

- **Image:** `unknown`
- **Container:** `whatsapp`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12352` → `12352` (tcp)
- **Networks:** elion

---

## phone

- **Image:** `unknown`
- **Container:** `phone`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12353` → `12353` (tcp)
- **Networks:** elion

---

## calendar

- **Image:** `unknown`
- **Container:** `calendar`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12354` → `12354` (tcp)
- **Networks:** elion

---

## social_media

- **Image:** `unknown`
- **Container:** `social_media`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12355` → `12355` (tcp)
- **Networks:** elion

---

## shop

- **Image:** `unknown`
- **Container:** `shop`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12356` → `12356` (tcp)
- **Networks:** elion

---

## html_creator

- **Image:** `unknown`
- **Container:** `html_creator`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12357` → `12357` (tcp)
- **Networks:** elion

---

## homepage_creator

- **Image:** `unknown`
- **Container:** `homepage_creator`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12358` → `12358` (tcp)
- **Networks:** elion

---

## stocks_crypto

- **Image:** `unknown`
- **Container:** `stocks_crypto`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12359` → `12359` (tcp)
- **Networks:** elion

---

## influencer

- **Image:** `unknown`
- **Container:** `influencer`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12360` → `12360` (tcp)
- **Networks:** elion

---

## unlock_master

- **Image:** `unknown`
- **Container:** `unlock_master`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12361` → `12361` (tcp)
- **Networks:** elion

---

## local_archiv

- **Image:** `unknown`
- **Container:** `local_archiv`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12362` → `12362` (tcp)
- **Networks:** elion

---

## custom_1

- **Image:** `unknown`
- **Container:** `custom_1`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12363` → `12363` (tcp)
- **Networks:** elion

---

## custom_2

- **Image:** `unknown`
- **Container:** `custom_2`
- **Compose File:** `docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12364` → `12364` (tcp)
- **Networks:** elion

---

## opena20-dashboard

- **Image:** `elion/opena20:latest`
- **Container:** `opena20-dashboard`
- **Compose File:** `19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** portier-network
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12349/health']

---

## nginx-gateway

- **Image:** `nginx:alpine`
- **Container:** `opena20-nginx`
- **Compose File:** `19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `80` → `80` (tcp)
  - `443` → `443` (tcp)
- **Networks:** portier-network
- **Dependencies:** opena20-dashboard

---

## redis-cache

- **Image:** `redis:alpine`
- **Container:** `opena20-redis`
- **Compose File:** `19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Networks:** portier-network

---

## prometheus

- **Image:** `prom/prometheus`
- **Container:** `opena20-prometheus`
- **Compose File:** `19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** portier-network

---
