"""
opena7 Mail Client
IMAP Fetcher, SMTP Sender, Message Classification, Attachment Handler
"""

import hashlib
import logging
import re
from datetime import UTC, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    import aioimaplib
    import aiosmtplib
except ImportError:
    aioimaplib = None
    aiosmtplib = None

from .config import config
from .models import (
    AttachmentInfo,
    EventLog,
    MailMessage,
    SentimentType,
)

logger = logging.getLogger(__name__)


class MailClassifier:
    """Classifies emails by sentiment, urgency, language"""

    @staticmethod
    def detect_language(text: str) -> str | None:
        """Simple language detection (EN/DE patterns)"""
        if not config.ENABLE_LANGUAGE_DETECTION:
            return None

        text_lower = text.lower()
        de_words = ["hallo", "guten", "danke", "anbei", "anhang", "betreff"]
        en_words = ["hello", "dear", "thanks", "attached", "subject", "regards"]

        de_count = sum(1 for w in de_words if w in text_lower)
        en_count = sum(1 for w in en_words if w in text_lower)

        if de_count > en_count:
            return "de"
        elif en_count > de_count:
            return "en"
        return None

    @staticmethod
    def classify_sentiment(subject: str, body: str) -> tuple[SentimentType, int]:
        """Classify sentiment and urgency"""
        if not config.ENABLE_SENTIMENT:
            return SentimentType.NEUTRAL, 5

        text = (subject + " " + body).lower()

        urgency_patterns = {
            r"urgent|asap|immediately|critical": 9,
            r"important|soon|high priority": 7,
            r"normal|regular": 5,
            r"when possible|low priority": 2,
        }

        urgency = 5
        for pattern, score in urgency_patterns.items():
            if re.search(pattern, text):
                urgency = score
                break

        sentiment_patterns = {
            SentimentType.URGENT: r"urgent|emergency|help|critical",
            SentimentType.POSITIVE: r"thank|great|excellent|happy|perfect",
            SentimentType.NEGATIVE: r"problem|issue|error|fail|upset|angry",
        }

        sentiment = SentimentType.NEUTRAL
        for sent, pattern in sentiment_patterns.items():
            if re.search(pattern, text):
                sentiment = sent
                break

        return sentiment, urgency

    @staticmethod
    def check_allowlist(sender: str) -> bool:
        """Check sender against allowlist"""
        sender_lower = sender.lower()

        for allowed in config.MAIL_ALLOWLIST:
            if allowed.startswith("@"):
                if sender_lower.endswith(allowed):
                    return True
            elif sender_lower == allowed:
                return True

        # Check blocklist
        for blocked in config.MAIL_BLOCKLIST:
            if blocked.lower() in sender_lower:
                return False

        return len(config.MAIL_ALLOWLIST) == 0


class AttachmentHandler:
    """Handles email attachment extraction & validation"""

    def __init__(self, archiv_base: str = "archivp"):
        self.archiv_base = Path(archiv_base)

    async def process_attachment(self, filename: str, content: bytes, msg_id: str) -> AttachmentInfo | None:
        """Process and store attachment"""

        # Check size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > config.MAIL_ATTACHMENT_LIMIT_MB:
            logger.warning(f"Attachment {filename} exceeds size limit ({size_mb:.1f} MB)")
            return None

        # Check extension
        file_ext = Path(filename).suffix.lower()
        if file_ext in config.DANGEROUS_EXTENSIONS:
            logger.warning(f"Dangerous file extension: {filename}")
            return AttachmentInfo(
                filename=filename,
                mime_type="application/octet-stream",
                size_bytes=len(content),
                scanned=True,
                safe=False,
                scan_result="Dangerous extension",
            )

        # Store attachment
        try:
            timestamp = datetime.now(UTC).strftime("%Y/%m/%d")
            artifact_dir = self.archiv_base / timestamp / "mail" / "attachments"
            artifact_dir.mkdir(parents=True, exist_ok=True)

            safe_filename = self._sanitize_filename(filename)
            filepath = artifact_dir / f"{msg_id}_{safe_filename}"

            with open(filepath, "wb") as f:
                f.write(content)

            sha256 = self._calculate_sha256(filepath)

            return AttachmentInfo(
                filename=filename,
                mime_type="application/octet-stream",
                size_bytes=len(content),
                sha256=sha256,
                path=str(filepath),
                scanned=config.SCAN_ATTACHMENTS,
                safe=True,
            )
        except Exception as e:
            logger.error(f"Failed to process attachment {filename}: {e}")
            return None

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove potentially dangerous characters from filename"""
        return re.sub(r"[^\w\s.-]", "_", filename)

    @staticmethod
    def _calculate_sha256(filepath: Path) -> str:
        """Calculate SHA256 of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class MailClient:
    """IMAP/SMTP mail client"""

    def __init__(self):
        self.imap_conn = None
        self.smtp_conn = None
        self.classifier = MailClassifier()
        self.attachment_handler = AttachmentHandler()
        self.event_logs: list[EventLog] = []

    async def connect_imap(self) -> bool:
        """Connect to IMAP server"""
        try:
            if not aioimaplib:
                logger.error("aioimaplib not installed")
                return False

            self.imap_conn = aioimaplib.IMAP4_SSL(config.MAIL_IMAP_HOST, config.MAIL_IMAP_PORT)

            await self.imap_conn.login(config.MAIL_USER, config.MAIL_PASS_ENVKEY)
            logger.info(f"✅ Connected to IMAP {config.MAIL_IMAP_HOST}:{config.MAIL_IMAP_PORT}")
            return True
        except Exception as e:
            logger.error(f"❌ IMAP connection failed: {e}")
            self.imap_conn = None
            return False

    async def connect_smtp(self) -> bool:
        """Connect to SMTP server"""
        try:
            if not aiosmtplib:
                logger.error("aiosmtplib not installed")
                return False

            self.smtp_conn = aiosmtplib.SMTP(
                hostname=config.MAIL_SMTP_HOST, port=config.MAIL_SMTP_PORT, use_tls=config.MAIL_SMTP_TLS
            )

            await self.smtp_conn.connect()
            await self.smtp_conn.login(config.MAIL_USER, config.MAIL_PASS_ENVKEY)
            logger.info(f"✅ Connected to SMTP {config.MAIL_SMTP_HOST}:{config.MAIL_SMTP_PORT}")
            return True
        except Exception as e:
            logger.error(f"❌ SMTP connection failed: {e}")
            self.smtp_conn = None
            return False

    async def disconnect(self):
        """Disconnect from servers"""
        try:
            if self.imap_conn:
                await self.imap_conn.logout()
                self.imap_conn = None
            if self.smtp_conn:
                await self.smtp_conn.quit()
                self.smtp_conn = None
            logger.info("✅ Disconnected from mail servers")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def fetch_messages(self, mailbox: str = "INBOX", max_count: int = 10) -> list[MailMessage]:
        """Fetch unread messages from mailbox"""

        if not self.imap_conn:
            await self.connect_imap()
            if not self.imap_conn:
                return []

        try:
            # Select mailbox
            await self.imap_conn.select(mailbox)

            # Search for unread
            typ, msg_nums = await self.imap_conn.search(None, "UNSEEN")
            msg_ids = msg_nums[0].split()[:max_count]

            messages = []
            for msg_id in msg_ids:
                try:
                    msg = await self._fetch_single_message(msg_id)
                    if msg:
                        messages.append(msg)
                except Exception as e:
                    logger.error(f"Error fetching message {msg_id}: {e}")

            return messages
        except Exception as e:
            logger.error(f"Failed to fetch messages: {e}")
            return []

    async def _fetch_single_message(self, msg_id: bytes) -> MailMessage | None:
        """Fetch and parse single message"""

        try:
            typ, msg_data = await self.imap_conn.fetch(msg_id, "(RFC822)")

            if not msg_data or not msg_data[0]:
                return None

            # Parse email
            import email

            msg = email.message_from_bytes(msg_data[0][1])

            subject = msg.get("Subject", "(no subject)")
            sender = msg.get("From", "unknown@example.org")

            # Check allowlist
            if not self.classifier.check_allowlist(sender):
                logger.warning(f"Sender {sender} not in allowlist")
                return None

            body_text = self._get_body_text(msg)
            body_preview = body_text[: config.MAIL_BODY_PREVIEW_CHARS]

            # Classify
            language = self.classifier.detect_language(subject + " " + body_text)
            sentiment, urgency = self.classifier.classify_sentiment(subject, body_text)

            # Extract attachments
            attachments = []
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if filename:
                        content = part.get_payload(decode=True)
                        att_info = await self.attachment_handler.process_attachment(filename, content, msg_id.decode())
                        if att_info:
                            attachments.append(att_info)

            return MailMessage(
                msg_id=msg_id.decode(),
                subject=subject,
                sender=sender,
                recipients=self._parse_email_list(msg.get("To", "")),
                cc=self._parse_email_list(msg.get("Cc", "")),
                bcc=self._parse_email_list(msg.get("Bcc", "")),
                date=msg.get("Date", datetime.now(UTC).isoformat().replace("+00:00", "Z")),
                body_text=body_text,
                body_preview=body_preview,
                attachments=attachments,
                language=language,
                sentiment=sentiment,
                urgency=urgency,
            )
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    async def send_message(self, to: str, subject: str, body_text: str, body_html: str | None = None) -> bool:
        """Send email via SMTP"""

        if not self.smtp_conn:
            await self.connect_smtp()
            if not self.smtp_conn:
                return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = config.MAIL_USER
            msg["To"] = to

            msg.attach(MIMEText(body_text, "plain"))
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            await self.smtp_conn.send_message(msg)
            logger.info(f"✅ Sent email to {to}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False

    @staticmethod
    def _get_body_text(msg) -> str:
        """Extract plain text from email"""

        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                except:
                    body = part.get_payload()
                break

        return body

    @staticmethod
    def _parse_email_list(email_str: str) -> list[str]:
        """Parse comma-separated email addresses"""
        if not email_str:
            return []

        import email.utils

        return [addr for name, addr in email.utils.getaddresses([email_str])]


# Global mail client instance
mail_client: MailClient | None = None


async def get_mail_client() -> MailClient:
    """Get or create mail client"""
    global mail_client
    if mail_client is None:
        mail_client = MailClient()
    return mail_client
