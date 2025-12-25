# MTProto / Ende‑zu‑Ende‑Verschlüsselung (Überblick)

**Zuletzt aktualisiert:** 2025-12-16

Dieses Dokument fasst die wesentlichen Konzepte von MTProto (Telegram) zusammen: Architektur, Verschlüsselung und Transport.

## 1. Komponenten

MTProto besteht aus drei Hauptkomponenten:

- **High‑Level (RPC/API):** Die Abfragesprache und Sitzungsverwaltung für API‑Aufrufe.
- **Kryptografische Schicht:** Autorisierungsschlüssel, Nachrichtenschlüssel, AES‑256‑Verschlüsselung; unterstützt Perfect Forward Secrecy.
- **Transportkomponente:** Überträgt verschlüsselte Container über HTTP/HTTPS, WS/WSS, TCP, UDP.

## 2. Nachrichtenformat

- Nachrichten bestehen aus: Nachrichten‑ID (64 Bit), Sequenznummer (32 Bit), Länge (32 Bit) und Nutzdaten (ausgerichtet auf 4 Byte).
- Vor dem Verschlüsseln wird ein interner Header hinzugefügt; außen werden Key‑ID (64 Bit) und Nachrichtenschlüssel (128 Bit) gesetzt.
- Der Nachrichtenschlüssel: mittlere 128 Bit des SHA256(Hash(message+meta)) plus 32 Bytes des Autorisierungs‑Schlüssels.

## 3. Autorisierung & Verschlüsselung

- Clients generieren einen Autorisierungsschlüssel (nahezu statisch) bei der ersten Nutzung.
- Nachrichten werden mit AES‑256 verschlüsselt; MTProto unterstützt Perfect Forward Secrecy (PFS) für zusätzliche Sicherheit.

## 4. Zeitsynchronisation

- Nachrichten‑IDs sind zeitbasiert; bei starker Zeitabweichung sendet der Server eine Zeitkorrektur und Salt.
- Nach Zeitkorrektur synchronisiert der Client und verwendet die neue Zeit für weitere Nachrichten.

## 5. Transportmodi

- Unterstützte Modi: TCP, WebSocket, WSS, HTTP, HTTPS, UDP.
- MTProto bietet optionale Features wie Transport‑Obfuscation und schnelle Antwort‑Mechanismen.

## 6. Implementierungshinweise für Entwickler

- Session‑Management: Sitzungen sind an Clients gebunden, nicht an einzelne Verbindungen.
- Wiederholung und Container: Verwenden Sie Container für mehrere RPC‑Aufrufe; berücksichtigen Sie gzip‑Unterstützung.
- Fehlerbehandlung: Zeitkorrektur, Nachrichtensequenzen und monotone IDs müssen beachtet werden.

---

**Weitere Ressourcen:**

- MTProto 2.0 Spezifikation (offizielle Dokumentation)
- TDLib Beispiele (Referenzimplementierungen)
