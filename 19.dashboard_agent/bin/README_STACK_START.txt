ELION Hyper-Dashboard – Start/Stop/Verify

Voraussetzung:
- venv313 unter: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai/venv313
- .env im Ordner 19.dashboard_agent (wird bei Start erzeugt, falls fehlt)

Start:
  cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent
  chmod +x bin/*.sh
  ./bin/start_all.sh

Stop:
  ./bin/stop_all.sh

Manuell einzeln:
  ./bin/start_opena19.sh   # Dashboard (12349)
  ./bin/start_opena2.sh    # Archivator (12345)
  ./bin/start_kordp.sh     # Kordinatport (12346)
  ./bin/start_opena1.sh    # Koordinator (12344)

Verifizieren:
  ./bin/verify_stack.sh

Swagger (mit Token aus .env über Authorize):
  http://127.0.0.1:12349/docs

UI (einfach):
  http://127.0.0.1:12349/ui/

