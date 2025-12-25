#!/usr/bin/env python3
"""
📥 IMAP Handler Module - PORTIER PAS-6.0
Handles email reading via IMAP with SSL/TLS support
"""

import email
import imaplib
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class IMAPHandler:
    """IMAP email reading functionality"""

    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.use_ssl = os.getenv("IMAP_USE_SSL", "true").lower() == "true"

        logger.info(f"📥 IMAPHandler initialized for {self.imap_server}:{self.imap_port}")

    async def connect(self) -> imaplib.IMAP4_SSL | None:
        """Connect to IMAP server"""
        try:
            if not self.email_address or not self.email_password:
                return None

            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.imap_port)

            mail.login(self.email_address, self.email_password)
            return mail

        except Exception as e:
            logger.error(f"❌ IMAP connection failed: {e}")
            return None

    async def get_inbox_emails(self, folder: str = "INBOX", limit: int = 10) -> dict[str, Any]:
        """Get emails from inbox"""
        try:
            mail = await self.connect()
            if not mail:
                return {"error": "connection_failed", "message": "Could not connect to IMAP server"}

            mail.select(folder)

            # Search for all emails
            status, messages = mail.search(None, "ALL")

            if status != "OK":
                return {"error": "search_failed", "message": "Could not search emails"}

            email_ids = messages[0].split()
            emails = []

            # Get latest emails (limit)
            for email_id in email_ids[-limit:]:
                try:
                    status, msg_data = mail.fetch(email_id, "(RFC822)")

                    if status == "OK":
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)

                        emails.append(
                            {
                                "id": email_id.decode(),
                                "subject": email_message.get("Subject", ""),
                                "from": email_message.get("From", ""),
                                "to": email_message.get("To", ""),
                                "date": email_message.get("Date", ""),
                                "body_preview": self._get_body_preview(email_message),
                            }
                        )

                except Exception as e:
                    logger.warning(f"⚠️ Error processing email {email_id}: {e}")
                    continue

            mail.close()
            mail.logout()

            return {
                "status": "success",
                "folder": folder,
                "count": len(emails),
                "emails": emails,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Get inbox failed: {e}")
            return {"error": "inbox_retrieval_failed", "message": str(e)}

    async def get_email_by_id(self, email_id: str, folder: str = "INBOX") -> dict[str, Any]:
        """Get specific email by ID"""
        try:
            mail = await self.connect()
            if not mail:
                return {"error": "connection_failed"}

            mail.select(folder)

            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                return {"error": "fetch_failed", "message": f"Could not fetch email {email_id}"}

            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            email_data = {
                "id": email_id,
                "subject": email_message.get("Subject", ""),
                "from": email_message.get("From", ""),
                "to": email_message.get("To", ""),
                "date": email_message.get("Date", ""),
                "body": self._get_email_body(email_message),
                "attachments": self._get_attachments(email_message),
            }

            mail.close()
            mail.logout()

            return {"status": "success", "email": email_data, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"❌ Get email by ID failed: {e}")
            return {"error": "email_retrieval_failed", "message": str(e)}

    def _get_body_preview(self, email_message: email.message.Message, max_chars: int = 200) -> str:
        """Extract email body preview"""
        try:
            body = self._get_email_body(email_message)
            return body[:max_chars] + "..." if len(body) > max_chars else body
        except Exception:
            return "[Preview not available]"

    def _get_email_body(self, email_message: email.message.Message) -> str:
        """Extract full email body"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                return email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
        except Exception:
            return "[Body not available]"

    def _get_attachments(self, email_message: email.message.Message) -> list[dict[str, str]]:
        """Extract attachment information"""
        attachments = []
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_disposition() == "attachment":
                        filename = part.get_filename()
                        if filename:
                            attachments.append(
                                {
                                    "filename": filename,
                                    "content_type": part.get_content_type(),
                                    "size": len(part.get_payload(decode=True)) if part.get_payload() else 0,
                                }
                            )
        except Exception as e:
            logger.warning(f"⚠️ Error extracting attachments: {e}")

        return attachments

    def test_connection(self) -> dict[str, Any]:
        """Test IMAP connection"""
        try:
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.imap_port)

            if self.email_address and self.email_password:
                mail.login(self.email_address, self.email_password)

            mail.logout()

            return {"status": "connected", "server": self.imap_server, "port": self.imap_port, "ssl": self.use_ssl}

        except Exception as e:
            return {"status": "failed", "error": str(e), "server": self.imap_server, "port": self.imap_port}
