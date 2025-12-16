# MTProto / End-to-End Encryption (Overview)

**Last updated:** 2025-12-16

This document summarizes the core concepts of MTProto (Telegram): architecture, encryption, and transport.

## 1. Components
MTProto is composed of three primary components:

- **High-level (RPC/API):** The query language and session management for API calls.
- **Cryptographic layer:** Authorization keys, message keys, AES‑256 encryption; supports Perfect Forward Secrecy.
- **Transport component:** Transmits encrypted containers over HTTP/HTTPS, WS/WSS, TCP, UDP.

## 2. Message format
- Messages include: message ID (64-bit), sequence number (32-bit), length (32-bit), and payload (4‑byte aligned).
- An internal header is added before encryption; externally a key ID (64-bit) and a 128‑bit message key are prepended.
- The message key is derived from the middle 128 bits of SHA256(message+meta) plus 32 bytes of the authorization key.

## 3. Authorization & Encryption
- Clients generate an authorization key on first run (long‑lived for a device).
- Messages are encrypted with AES‑256; MTProto supports PFS for additional security.

## 4. Time synchronization
- Message IDs are time‑based; the server may send time correction and salt when significant drift is detected.
- Clients apply time correction and continue with adjusted message IDs.

## 5. Transport modes
- Supported transports: TCP, WebSocket, WSS, HTTP, HTTPS, UDP.
- MTProto offers optional features like transport obfuscation and fast reply.

## 6. Implementation notes for developers
- Session management: sessions are bound to the client application rather than a single connection.
- Use containers for batching RPC calls; consider gzip support.
- Handle time corrections, monotonic message IDs, and sequence validation.

---

**References:**
- MTProto 2.0 specification
- TDLib and MadelineProto reference implementations