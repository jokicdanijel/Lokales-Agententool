# Agent Fleet Inventory Report

**Generated:** 2025-12-24 10:20:50 UTC

**Total Services:** 185

---

## otel-collector

**Status:** ⚪ NOT_FOUND

- **Image:** `otel/opentelemetry-collector:latest`
- **Container:** `otel-collector`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.otel.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `4317` → `4317` (tcp)
  - `4318` → `4318` (tcp)
  - `13133` → `13133` (tcp)

---

## opena20-dashboard

**Status:** ⚪ NOT_FOUND

- **Image:** `opena20-dashboard:local`
- **Container:** `opena20-dashboard`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Health Check:** ['CMD-SHELL', 'curl -f http://localhost:12349/health || exit 1']

---

## prometheus

**Status:** 🟢 RUNNING (ID: `b91b057bf9`)

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost:9090/-/healthy']

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3001` → `3000` (tcp)
- **Networks:** elion
- **Dependencies:** prometheus
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:3000/api/health']

---

## portier

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `portier`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12344/health']

---

## archivator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12345/health']

---

## telegram

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `telegram`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12346` → `12346` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12346/health']

---

## inference

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `inference`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12348` → `12348` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12348/health']

---

## browser

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `browser`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** elion

---

## vscode

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `vscode`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12350` → `12350` (tcp)
- **Networks:** elion

---

## email

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `email`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** elion

---

## whatsapp

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `whatsapp`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12352` → `12352` (tcp)
- **Networks:** elion

---

## phone

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `phone`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12353` → `12353` (tcp)
- **Networks:** elion

---

## calendar

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `calendar`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12354` → `12354` (tcp)
- **Networks:** elion

---

## social_media

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `social_media`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12355` → `12355` (tcp)
- **Networks:** elion

---

## shop

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `shop`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12356` → `12356` (tcp)
- **Networks:** elion

---

## html_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `html_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12357` → `12357` (tcp)
- **Networks:** elion

---

## homepage_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `homepage_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12358` → `12358` (tcp)
- **Networks:** elion

---

## stocks_crypto

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `stocks_crypto`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12359` → `12359` (tcp)
- **Networks:** elion

---

## influencer

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `influencer`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12360` → `12360` (tcp)
- **Networks:** elion

---

## unlock_master

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `unlock_master`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12361` → `12361` (tcp)
- **Networks:** elion

---

## local_archiv

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `local_archiv`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12362` → `12362` (tcp)
- **Networks:** elion

---

## custom_1

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12363` → `12363` (tcp)
- **Networks:** elion

---

## custom_2

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12364` → `12364` (tcp)
- **Networks:** elion

---

## postgres

**Status:** ⚪ NOT_FOUND

- **Image:** `postgres:16-alpine`
- **Container:** `eden-postgres`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `5432` → `5432` (tcp)
- **Networks:** eden-network
- **Health Check:** ['CMD-SHELL', 'pg_isready -U eden_user -d eden']

---

## redis

**Status:** ⚪ NOT_FOUND

- **Image:** `redis:7-alpine`
- **Container:** `eden-redis`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `6379` → `6379` (tcp)
- **Networks:** eden-network
- **Health Check:** ['CMD', 'redis-cli', 'ping']

---

## vault

**Status:** ⚪ NOT_FOUND

- **Image:** `hashicorp/vault:1.15`
- **Container:** `eden-vault`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `8200` → `8200` (tcp)
- **Networks:** eden-network

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-opena1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** eden-network
- **Dependencies:** postgres, redis
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12344/health']

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-opena2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** eden-network
- **Dependencies:** postgres, redis

---

## auth

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-auth`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12370` → `12370` (tcp)
- **Networks:** eden-network
- **Dependencies:** postgres, redis

---

## billing

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-billing`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12371` → `12371` (tcp)
- **Networks:** eden-network
- **Dependencies:** postgres, auth

---

## website

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-website`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12372` → `12372` (tcp)
- **Networks:** eden-network

---

## dashboard

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-dashboard`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** eden-network
- **Dependencies:** opena1, auth

---

## workflow

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `eden-workflow`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12368` → `12368` (tcp)
- **Networks:** eden-network
- **Dependencies:** postgres, opena1, opena2

---

## nginx

**Status:** ⚪ NOT_FOUND

- **Image:** `nginx:alpine`
- **Container:** `eden-nginx`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `80` → `80` (tcp)
  - `443` → `443` (tcp)
- **Networks:** eden-network
- **Dependencies:** website, dashboard, auth, billing

---

## prometheus

**Status:** ⚪ NOT_FOUND

- **Image:** `prom/prometheus:latest`
- **Container:** `eden-prometheus`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** eden-network

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `eden-grafana`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.production.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `3000` (tcp)
- **Networks:** eden-network
- **Dependencies:** prometheus

---

## otel-collector

**Status:** ⚪ NOT_FOUND

- **Image:** `otel/opentelemetry-collector:latest`
- **Container:** `otel-collector`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.tracing.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `4317` → `4317` (tcp)
  - `4318` → `4318` (tcp)
  - `8888` → `8888` (tcp)
  - `8889` → `8889` (tcp)
- **Networks:** elion

---

## jaeger

**Status:** 🟢 RUNNING (ID: `625067e4ae`)

- **Image:** `jaegertracing/all-in-one:latest`
- **Container:** `jaeger`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.tracing.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `16686` → `16686` (tcp)
  - `14250` → `14250` (tcp)
  - `14268` → `14268` (tcp)
- **Networks:** elion

---

## prometheus

**Status:** ⚪ CREATED (ID: `67a8c9005c`)

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.tracing.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** elion

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/docker-compose.tracing.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `3000` → `3000` (tcp)
- **Networks:** elion

---

## opena4_telegram

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena4_telegram`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/3.opena4_telegram/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12347` → `12347` (tcp)
- **Networks:** portier_net

---

## otel-collector

**Status:** ⚪ NOT_FOUND

- **Image:** `otel/opentelemetry-collector:latest`
- **Container:** `otel-collector`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/docker-compose.otel.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `4317` → `4317` (tcp)
  - `4318` → `4318` (tcp)
  - `13133` → `13133` (tcp)

---

## opena20-dashboard

**Status:** ⚪ NOT_FOUND

- **Image:** `elion/opena20:latest`
- **Container:** `opena20-dashboard`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** portier-network
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12349/health']

---

## nginx-gateway

**Status:** ⚪ NOT_FOUND

- **Image:** `nginx:alpine`
- **Container:** `opena20-nginx`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `80` → `80` (tcp)
  - `443` → `443` (tcp)
- **Networks:** portier-network
- **Dependencies:** opena20-dashboard

---

## redis-cache

**Status:** ⚪ NOT_FOUND

- **Image:** `redis:alpine`
- **Container:** `opena20-redis`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Networks:** portier-network

---

## prometheus

**Status:** ⚪ NOT_FOUND

- **Image:** `prom/prometheus`
- **Container:** `opena20-prometheus`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** portier-network

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.openwebui/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `8080` (tcp)

---

## api

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `api`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/telegram_multi/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `8000` → `8000` (tcp)
- **Networks:** telegram_net
- **Dependencies:** postgres, redis

---

## postgres

**Status:** ⚪ NOT_FOUND

- **Image:** `postgres:16-alpine`
- **Container:** `postgres`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/telegram_multi/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `5432` → `5432` (tcp)
- **Networks:** telegram_net

---

## redis

**Status:** ⚪ NOT_FOUND

- **Image:** `redis:7-alpine`
- **Container:** `redis`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/telegram_multi/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `6379` → `6379` (tcp)
- **Networks:** telegram_net

---

## worker

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `worker`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/telegram_multi/docker-compose.yml`
- **Restart Policy:** `no`
- **Networks:** telegram_net
- **Dependencies:** redis

---

## opena7

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena7-mail`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/6.opena7_email/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12350` (tcp)
- **Networks:** portier_net
- **Dependencies:** opena1, opena2
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12350/health']

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA1_IMAGE:-localhost:5000/opena1:latest}`
- **Container:** `opena1-coordinator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/6.opena7_email/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12344` (tcp)
- **Networks:** portier_net

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA2_IMAGE:-localhost:5000/opena2:latest}`
- **Container:** `opena2-archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/6.opena7_email/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12345` (tcp)
- **Networks:** portier_net

---

## prometheus

**Status:** 🟢 RUNNING (ID: `b91b057bf9`)

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost:9090/-/healthy']

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3001` → `3000` (tcp)
- **Networks:** elion
- **Dependencies:** prometheus
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:3000/api/health']

---

## portier

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `portier`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12344/health']

---

## archivator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12345/health']

---

## telegram

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `telegram`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12346` → `12346` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12346/health']

---

## inference

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `inference`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12348` → `12348` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12348/health']

---

## browser

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `browser`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** elion

---

## vscode

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `vscode`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12350` → `12350` (tcp)
- **Networks:** elion

---

## email

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `email`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** elion

---

## whatsapp

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `whatsapp`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12352` → `12352` (tcp)
- **Networks:** elion

---

## phone

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `phone`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12353` → `12353` (tcp)
- **Networks:** elion

---

## calendar

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `calendar`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12354` → `12354` (tcp)
- **Networks:** elion

---

## social_media

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `social_media`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12355` → `12355` (tcp)
- **Networks:** elion

---

## shop

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `shop`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12356` → `12356` (tcp)
- **Networks:** elion

---

## html_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `html_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12357` → `12357` (tcp)
- **Networks:** elion

---

## homepage_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `homepage_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12358` → `12358` (tcp)
- **Networks:** elion

---

## stocks_crypto

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `stocks_crypto`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12359` → `12359` (tcp)
- **Networks:** elion

---

## influencer

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `influencer`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12360` → `12360` (tcp)
- **Networks:** elion

---

## unlock_master

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `unlock_master`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12361` → `12361` (tcp)
- **Networks:** elion

---

## local_archiv

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `local_archiv`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12362` → `12362` (tcp)
- **Networks:** elion

---

## custom_1

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12363` → `12363` (tcp)
- **Networks:** elion

---

## custom_2

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12364` → `12364` (tcp)
- **Networks:** elion

---

## prometheus

**Status:** 🟢 RUNNING (ID: `b91b057bf9`)

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost:9090/-/healthy']

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3001` → `3000` (tcp)
- **Networks:** elion
- **Dependencies:** prometheus
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:3000/api/health']

---

## portier

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `portier`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12344/health']

---

## archivator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12345/health']

---

## telegram

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `telegram`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12346` → `12346` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12346/health']

---

## inference

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `inference`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12348` → `12348` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12348/health']

---

## browser

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `browser`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** elion

---

## vscode

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `vscode`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12350` → `12350` (tcp)
- **Networks:** elion

---

## email

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `email`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** elion

---

## whatsapp

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `whatsapp`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12352` → `12352` (tcp)
- **Networks:** elion

---

## phone

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `phone`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12353` → `12353` (tcp)
- **Networks:** elion

---

## calendar

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `calendar`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12354` → `12354` (tcp)
- **Networks:** elion

---

## social_media

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `social_media`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12355` → `12355` (tcp)
- **Networks:** elion

---

## shop

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `shop`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12356` → `12356` (tcp)
- **Networks:** elion

---

## html_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `html_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12357` → `12357` (tcp)
- **Networks:** elion

---

## homepage_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `homepage_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12358` → `12358` (tcp)
- **Networks:** elion

---

## stocks_crypto

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `stocks_crypto`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12359` → `12359` (tcp)
- **Networks:** elion

---

## influencer

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `influencer`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12360` → `12360` (tcp)
- **Networks:** elion

---

## unlock_master

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `unlock_master`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12361` → `12361` (tcp)
- **Networks:** elion

---

## local_archiv

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `local_archiv`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12362` → `12362` (tcp)
- **Networks:** elion

---

## custom_1

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12363` → `12363` (tcp)
- **Networks:** elion

---

## custom_2

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12364` → `12364` (tcp)
- **Networks:** elion

---

## opena6

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena6-browser`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/5.opena6_browser/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12349` (tcp)
- **Networks:** portier_net
- **Dependencies:** opena1, opena2
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12349/health']

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA1_IMAGE:-localhost:5000/opena1:latest}`
- **Container:** `opena1-coordinator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/5.opena6_browser/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12344` (tcp)
- **Networks:** portier_net

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA2_IMAGE:-localhost:5000/opena2:latest}`
- **Container:** `opena2-archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/5.opena6_browser/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12345` (tcp)
- **Networks:** portier_net

---

## opena8-whatsapp

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena8-whatsapp`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/7.opena8_whatsapp/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** portier_net
- **Dependencies:** opena1, opena2
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12351/health']

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `localhost:5000/opena1:latest`
- **Container:** `opena1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/7.opena8_whatsapp/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** portier_net

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `localhost:5000/opena2:latest`
- **Container:** `opena2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/7.opena8_whatsapp/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** portier_net

---

## reverse-proxy

**Status:** 🟢 RUNNING (ID: `5d8dc64271`)

- **Image:** `unknown`
- **Container:** `opena4-reverse-proxy`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel/docker-compose.proxy.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)

---

## n8n

**Status:** 🟢 RUNNING (ID: `dba5885660`)

- **Image:** `n8nio/n8n:stable`
- **Container:** `local_n8n`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/dev/n8n/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `5678` (tcp)

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:latest`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro/docker-compose.simple.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `11434` → `11434` (tcp)
- **Networks:** agent-network

---

## openwebui

**Status:** ⚪ NOT_FOUND

- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Container:** `openwebui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro/docker-compose.simple.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `8080` (tcp)
- **Networks:** agent-network
- **Dependencies:** ollama

---

## localagent-pro

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `localagent-pro`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `8001` → `8001` (tcp)
- **Networks:** agent-network
- **Dependencies:** ollama

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:latest`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `11434` → `11434` (tcp)
- **Networks:** agent-network

---

## openwebui

**Status:** ⚪ NOT_FOUND

- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Container:** `openwebui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `8080` (tcp)
- **Networks:** agent-network
- **Dependencies:** ollama, localagent-pro
- **Health Check:** ['CMD', 'curl', '-f', 'http://0.0.0.0:8080/health || exit 1']

---

## opena4_telegram

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena4_telegram`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/3.opena4_telegram/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12347` → `12347` (tcp)
- **Networks:** portier_net

---

## opena20-dashboard

**Status:** ⚪ NOT_FOUND

- **Image:** `elion/opena20:latest`
- **Container:** `opena20-dashboard`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** portier-network
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12349/health']

---

## nginx-gateway

**Status:** ⚪ NOT_FOUND

- **Image:** `nginx:alpine`
- **Container:** `opena20-nginx`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `80` → `80` (tcp)
  - `443` → `443` (tcp)
- **Networks:** portier-network
- **Dependencies:** opena20-dashboard

---

## redis-cache

**Status:** ⚪ NOT_FOUND

- **Image:** `redis:alpine`
- **Container:** `opena20-redis`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Networks:** portier-network

---

## prometheus

**Status:** ⚪ NOT_FOUND

- **Image:** `prom/prometheus`
- **Container:** `opena20-prometheus`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** portier-network

---

## localagent-pro

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `localagent-pro`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `8001` → `8001` (tcp)
- **Networks:** localagent-network
- **Dependencies:** ollama
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:8001/health']

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:latest`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `11434` → `11434` (tcp)
- **Networks:** localagent-network
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:11434/api/tags']

---

## prometheus

**Status:** ⚪ CREATED (ID: `67a8c9005c`)

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** localagent-network

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3001` → `3000` (tcp)
- **Networks:** localagent-network
- **Dependencies:** prometheus

---

## opena7

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena7-mail`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/6.opena7_email/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12350` (tcp)
- **Networks:** portier_net
- **Dependencies:** opena1, opena2
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12350/health']

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA1_IMAGE:-localhost:5000/opena1:latest}`
- **Container:** `opena1-coordinator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/6.opena7_email/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12344` (tcp)
- **Networks:** portier_net

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA2_IMAGE:-localhost:5000/opena2:latest}`
- **Container:** `opena2-archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/6.opena7_email/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12345` (tcp)
- **Networks:** portier_net

---

## opena20-dashboard

**Status:** ⚪ NOT_FOUND

- **Image:** `elion/opena20:latest`
- **Container:** `opena20-dashboard`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent.BROKEN_20251130_2037/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** portier-network
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12349/health']

---

## nginx-gateway

**Status:** ⚪ NOT_FOUND

- **Image:** `nginx:alpine`
- **Container:** `opena20-nginx`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent.BROKEN_20251130_2037/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `80` → `80` (tcp)
  - `443` → `443` (tcp)
- **Networks:** portier-network
- **Dependencies:** opena20-dashboard

---

## redis-cache

**Status:** ⚪ NOT_FOUND

- **Image:** `redis:alpine`
- **Container:** `opena20-redis`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent.BROKEN_20251130_2037/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Networks:** portier-network

---

## prometheus

**Status:** ⚪ NOT_FOUND

- **Image:** `prom/prometheus`
- **Container:** `opena20-prometheus`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/19.opena20_dashboard_agent.BROKEN_20251130_2037/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** portier-network

---

## prometheus

**Status:** 🟢 RUNNING (ID: `b91b057bf9`)

- **Image:** `prom/prometheus:latest`
- **Container:** `prometheus-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `9090` → `9090` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost:9090/-/healthy']

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/grafana:latest`
- **Container:** `grafana-elion`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3001` → `3000` (tcp)
- **Networks:** elion
- **Dependencies:** prometheus
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:3000/api/health']

---

## portier

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `portier`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12344/health']

---

## archivator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12345/health']

---

## telegram

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `telegram`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12346` → `12346` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12346/health']

---

## inference

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `inference`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `12348` → `12348` (tcp)
- **Networks:** elion
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12348/health']

---

## browser

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `browser`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12349` → `12349` (tcp)
- **Networks:** elion

---

## vscode

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `vscode`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12350` → `12350` (tcp)
- **Networks:** elion

---

## email

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `email`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** elion

---

## whatsapp

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `whatsapp`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12352` → `12352` (tcp)
- **Networks:** elion

---

## phone

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `phone`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12353` → `12353` (tcp)
- **Networks:** elion

---

## calendar

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `calendar`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12354` → `12354` (tcp)
- **Networks:** elion

---

## social_media

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `social_media`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12355` → `12355` (tcp)
- **Networks:** elion

---

## shop

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `shop`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12356` → `12356` (tcp)
- **Networks:** elion

---

## html_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `html_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12357` → `12357` (tcp)
- **Networks:** elion

---

## homepage_creator

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `homepage_creator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12358` → `12358` (tcp)
- **Networks:** elion

---

## stocks_crypto

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `stocks_crypto`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12359` → `12359` (tcp)
- **Networks:** elion

---

## influencer

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `influencer`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12360` → `12360` (tcp)
- **Networks:** elion

---

## unlock_master

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `unlock_master`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12361` → `12361` (tcp)
- **Networks:** elion

---

## local_archiv

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `local_archiv`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12362` → `12362` (tcp)
- **Networks:** elion

---

## custom_1

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12363` → `12363` (tcp)
- **Networks:** elion

---

## custom_2

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `custom_2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/Unbenannter Ordner/docker-compose.prod.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12364` → `12364` (tcp)
- **Networks:** elion

---

## opena6

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena6-browser`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/5.opena6_browser/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12349` (tcp)
- **Networks:** portier_net
- **Dependencies:** opena1, opena2
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12349/health']

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA1_IMAGE:-localhost:5000/opena1:latest}`
- **Container:** `opena1-coordinator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/5.opena6_browser/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12344` (tcp)
- **Networks:** portier_net

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `${OPENA2_IMAGE:-localhost:5000/opena2:latest}`
- **Container:** `opena2-archivator`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/5.opena6_browser/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `127.0.0.1` → `12345` (tcp)
- **Networks:** portier_net

---

## opena8-whatsapp

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `opena8-whatsapp`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/7.opena8_whatsapp/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12351` → `12351` (tcp)
- **Networks:** portier_net
- **Dependencies:** opena1, opena2
- **Health Check:** ['CMD', 'curl', '-f', 'http://localhost:12351/health']

---

## opena1

**Status:** ⚪ NOT_FOUND

- **Image:** `localhost:5000/opena1:latest`
- **Container:** `opena1`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/7.opena8_whatsapp/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12344` → `12344` (tcp)
- **Networks:** portier_net

---

## opena2

**Status:** ⚪ NOT_FOUND

- **Image:** `localhost:5000/opena2:latest`
- **Container:** `opena2`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/7.opena8_whatsapp/docker-compose.yml`
- **Restart Policy:** `no`
- **Ports:**
  - `12345` → `12345` (tcp)
- **Networks:** portier_net

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:latest`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/2.opena3_openwebui/LocalAgent-Pro/docker-compose.simple.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `11434` → `11434` (tcp)
- **Networks:** agent-network

---

## openwebui

**Status:** ⚪ NOT_FOUND

- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Container:** `openwebui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/2.opena3_openwebui/LocalAgent-Pro/docker-compose.simple.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `8080` (tcp)
- **Networks:** agent-network
- **Dependencies:** ollama

---

## localagent-pro

**Status:** ⚪ NOT_FOUND

- **Image:** `unknown`
- **Container:** `localagent-pro`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/2.opena3_openwebui/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `8001` → `8001` (tcp)
- **Networks:** agent-network
- **Dependencies:** ollama

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:latest`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/2.opena3_openwebui/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `11434` → `11434` (tcp)
- **Networks:** agent-network

---

## openwebui

**Status:** ⚪ NOT_FOUND

- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Container:** `openwebui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/2.opena3_openwebui/LocalAgent-Pro/docker-compose.yml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `8080` (tcp)
- **Networks:** agent-network
- **Dependencies:** ollama, localagent-pro
- **Health Check:** ['CMD', 'curl', '-f', 'http://0.0.0.0:8080/health || exit 1']

---

## stable-diffusion-webui

**Status:** ⚪ NOT_FOUND

- **Image:** `ghcr.io/neggles/sd-webui-docker:latest`
- **Container:** `stable-diffusion-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.a1111-test.yaml`
- **Restart Policy:** `unless-stopped`

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `unknown`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.a1111-test.yaml`
- **Restart Policy:** `no`

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `unknown`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.gpu.yaml`
- **Restart Policy:** `no`

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:${OLLAMA_DOCKER_TAG-rocm}`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.amdgpu.yaml`
- **Restart Policy:** `no`

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `unknown`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.api.yaml`
- **Restart Policy:** `no`
- **Ports:**
  - `${OLLAMA_WEBAPI_PORT-11434}` → `11434` (tcp)

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/otel-lgtm:latest`
- **Container:** `lgtm`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.otel.yaml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `3000` (tcp)
  - `4317` → `4317` (tcp)
  - `4318` → `4318` (tcp)

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `ghcr.io/open-webui/open-webui:${WEBUI_DOCKER_TAG-main}`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.otel.yaml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `${OPEN_WEBUI_PORT-8088}` → `8080` (tcp)
- **Dependencies:** grafana

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:${OLLAMA_DOCKER_TAG-latest}`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.yaml`
- **Restart Policy:** `unless-stopped`

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `ghcr.io/open-webui/open-webui:${WEBUI_DOCKER_TAG-main}`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.yaml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `${OPEN_WEBUI_PORT-3000}` → `8080` (tcp)
- **Dependencies:** ollama

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `unknown`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.data.yaml`
- **Restart Policy:** `no`

---

## playwright

**Status:** ⚪ NOT_FOUND

- **Image:** `mcr.microsoft.com/playwright:v1.49.1-noble`
- **Container:** `playwright`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.playwright.yaml`
- **Restart Policy:** `no`

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `unknown`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/open-webui-0.6.40/docker-compose.playwright.yaml`
- **Restart Policy:** `no`

---

## stable-diffusion-webui

**Status:** ⚪ NOT_FOUND

- **Image:** `ghcr.io/neggles/sd-webui-docker:latest`
- **Container:** `stable-diffusion-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.a1111-test.yaml`
- **Restart Policy:** `unless-stopped`

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `unknown`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.a1111-test.yaml`
- **Restart Policy:** `no`

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `unknown`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.gpu.yaml`
- **Restart Policy:** `no`

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:${OLLAMA_DOCKER_TAG-rocm}`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.amdgpu.yaml`
- **Restart Policy:** `no`

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `unknown`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.api.yaml`
- **Restart Policy:** `no`
- **Ports:**
  - `${OLLAMA_WEBAPI_PORT-11434}` → `11434` (tcp)

---

## grafana

**Status:** ⚪ NOT_FOUND

- **Image:** `grafana/otel-lgtm:latest`
- **Container:** `lgtm`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.otel.yaml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `3000` → `3000` (tcp)
  - `4317` → `4317` (tcp)
  - `4318` → `4318` (tcp)

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `ghcr.io/open-webui/open-webui:${WEBUI_DOCKER_TAG-main}`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.otel.yaml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `${OPEN_WEBUI_PORT-8088}` → `8080` (tcp)
- **Dependencies:** grafana

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `ollama/ollama:${OLLAMA_DOCKER_TAG-latest}`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.yaml`
- **Restart Policy:** `unless-stopped`

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `ghcr.io/open-webui/open-webui:${WEBUI_DOCKER_TAG-main}`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.yaml`
- **Restart Policy:** `unless-stopped`
- **Ports:**
  - `${OPEN_WEBUI_PORT-3000}` → `8080` (tcp)
- **Dependencies:** ollama

---

## ollama

**Status:** 🟢 RUNNING (ID: `4f9d7dcac4`)

- **Image:** `unknown`
- **Container:** `ollama`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.data.yaml`
- **Restart Policy:** `no`

---

## playwright

**Status:** ⚪ NOT_FOUND

- **Image:** `mcr.microsoft.com/playwright:v1.49.1-noble`
- **Container:** `playwright`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.playwright.yaml`
- **Restart Policy:** `no`

---

## open-webui

**Status:** 🟢 RUNNING (ID: `8de7895d89`)

- **Image:** `unknown`
- **Container:** `open-webui`
- **Compose File:** `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/start/open-webui-0.6.40/docker-compose.playwright.yaml`
- **Restart Policy:** `no`

---
