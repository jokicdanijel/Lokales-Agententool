"""
Mail Agent - Beispiel-Implementation für E-Mail-Funktionalität.
Zeigt wie ein konkreter Agent die AgentBase nutzt.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone

from ..agent_base import AgentBase, AgentCapability, AgentStatus

logger = logging.getLogger("mail_agent")


class MailAgent(AgentBase):
    """
    E-Mail Agent - kann Mails senden/empfangen/lesen.
    
    Capabilities: EMAIL
    Commands:
    - send_mail: Sendet eine E-Mail
    - list_inbox: Listet Inbox-Mails
    - read_mail: Liest eine spezifische Mail
    """
    
    def __init__(self, memory_system=None):
        super().__init__(
            agent_id="mail_agent",
            capabilities=[AgentCapability.EMAIL],
            memory_system=memory_system
        )
        
        # Agent-spezifische Konfiguration
        self.smtp_config = {
            "host": "smtp.example.com",
            "port": 587,
            "use_tls": True
        }
        
        self.imap_config = {
            "host": "imap.example.com",
            "port": 993,
            "use_ssl": True
        }
    
    async def initialize(self) -> None:
        """Initialisierung: SMTP/IMAP-Verbindungen prüfen"""
        await super().initialize()
        
        # TODO: Tatsächliche SMTP/IMAP-Verbindung herstellen
        logger.info("MailAgent: Checking SMTP/IMAP connections...")
        
        # Simulated connection check
        await self.store_memory("last_init", datetime.now(timezone.utc).isoformat())
        
        self.status = AgentStatus.READY
        logger.info("MailAgent initialized and ready")
    
    async def execute(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt E-Mail-Commands aus.
        
        Args:
            command: "send_mail", "list_inbox", "read_mail"
            params: Command-spezifische Parameter
            
        Returns:
            Dict: {"status": "success|error", "data": ..., "error": None}
        """
        self.status = AgentStatus.BUSY
        
        try:
            if command == "send_mail":
                result = await self._send_mail(params)
            elif command == "list_inbox":
                result = await self._list_inbox(params)
            elif command == "read_mail":
                result = await self._read_mail(params)
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown command: {command}",
                    "data": None
                }
            
            self.status = AgentStatus.READY
            return result
        
        except Exception as e:
            logger.error(f"MailAgent command execution failed: {e}")
            self.status = AgentStatus.ERROR
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health-Check: SMTP/IMAP-Verbindungen prüfen.
        """
        # TODO: Echte Verbindungsprüfung
        return {
            "status": "healthy",
            "details": {
                "smtp": {"connected": True, "host": self.smtp_config["host"]},
                "imap": {"connected": True, "host": self.imap_config["host"]},
                "last_init": await self.retrieve_memory("last_init")
            }
        }
    
    # --- Private Command Implementations ---
    
    async def _send_mail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sendet eine E-Mail.
        
        Params:
            to: Empfänger-Adresse
            subject: Betreff
            body: Nachrichtentext
            attachments: Liste von Anhängen (optional)
        """
        # Validierung
        required = ["to", "subject", "body"]
        for field in required:
            if field not in params:
                return {
                    "status": "error",
                    "error": f"Missing required field: {field}",
                    "data": None
                }
        
        # TODO: Tatsächliches SMTP-Senden
        logger.info(f"Sending mail to {params['to']}: {params['subject']}")
        
        # Simulated send
        mail_id = f"mail_{datetime.now(timezone.utc).timestamp()}"
        
        # Im Memory speichern
        await self.store_memory(f"sent_{mail_id}", {
            "to": params["to"],
            "subject": params["subject"],
            "sent_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "status": "success",
            "data": {
                "mail_id": mail_id,
                "to": params["to"],
                "subject": params["subject"],
                "sent_at": datetime.now(timezone.utc).isoformat()
            },
            "error": None
        }
    
    async def _list_inbox(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Listet Inbox-Mails.
        
        Params:
            limit: Max. Anzahl Mails (default: 10)
            unread_only: Nur ungelesene (default: False)
        """
        limit = params.get("limit", 10)
        unread_only = params.get("unread_only", False)
        
        # TODO: Tatsächliches IMAP-Lesen
        logger.info(f"Listing inbox (limit={limit}, unread_only={unread_only})")
        
        # Simulated inbox
        mails = [
            {
                "id": f"mail_{i}",
                "from": f"sender{i}@example.com",
                "subject": f"Test Mail {i}",
                "date": datetime.now(timezone.utc).isoformat(),
                "read": i % 2 == 0
            }
            for i in range(1, min(limit + 1, 6))
        ]
        
        if unread_only:
            mails = [m for m in mails if not m["read"]]
        
        return {
            "status": "success",
            "data": {
                "mails": mails,
                "count": len(mails)
            },
            "error": None
        }
    
    async def _read_mail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Liest eine spezifische Mail.
        
        Params:
            mail_id: Mail-ID
        """
        mail_id = params.get("mail_id")
        if not mail_id:
            return {
                "status": "error",
                "error": "Missing required field: mail_id",
                "data": None
            }
        
        # TODO: Tatsächliches IMAP-Lesen
        logger.info(f"Reading mail: {mail_id}")
        
        # Simulated mail content
        mail_content = {
            "id": mail_id,
            "from": "sender@example.com",
            "to": "you@example.com",
            "subject": "Test Mail",
            "body": "This is a test mail body.",
            "date": datetime.now(timezone.utc).isoformat(),
            "read": True
        }
        
        return {
            "status": "success",
            "data": mail_content,
            "error": None
        }
