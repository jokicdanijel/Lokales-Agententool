#!/usr/bin/env python3
"""
📤 SMTP Sender Module - PORTIER PAS-6.0
Handles email sending via SMTP with authentication
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SMTPSender:
    """SMTP email sending functionality"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        
        logger.info(f"📤 SMTPSender initialized for {self.smtp_server}:{self.smtp_port}")
    
    async def send_email(self, to: str, subject: str, body: str, 
                        from_name: str = "", cc: List[str] = None, 
                        bcc: List[str] = None, html: bool = False) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            if not self.email_address or not self.email_password:
                return {
                    "error": "smtp_not_configured",
                    "message": "SMTP credentials not configured"
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((from_name or "Email Agent", self.email_address))
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.email_address, self.email_password)
            
            # Recipients list
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.send_message(msg, to_addrs=recipients)
            server.quit()
            
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
                "message_id": msg.get('Message-ID', '')
            }
            
        except Exception as e:
            logger.error(f"❌ SMTP send failed: {e}")
            return {
                "error": "send_failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            if self.email_address and self.email_password:
                server.login(self.email_address, self.email_password)
            
            server.quit()
            
            return {
                "status": "connected",
                "server": self.smtp_server,
                "port": self.smtp_port,
                "tls": self.use_tls
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "server": self.smtp_server,
                "port": self.smtp_port
            }