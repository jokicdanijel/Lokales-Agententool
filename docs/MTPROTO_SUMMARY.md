# MTProto — Kurzfassung für Entwickler

- MTProto = API (RPC) + Kryptoschicht + Transport.
- Nachrichten: messageId (64), seq (32), length (32), payload (4‑byte aligned).
- Verschlüsselung: AES‑256, MessageKey (128 Bit), AuthorizationKey (long‑lived); PFS unterstützt.
- Transports: TCP, WS, WSS, HTTP, HTTPS, UDP; Unterstützung für Obfuscation/Gzip.
- Implementations‑Hints: Zeit‑Sync, session‑bound IDs, Version 2.0 (aktuell).

Mehr: `docs/MTPROTO_OVERVIEW.md`
