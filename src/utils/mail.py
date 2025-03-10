import email
import requests
import time
from dataclasses import dataclass
from imapclient import IMAPClient
from typing import List, Optional, Tuple
from src.utils.ui import status_print
from bs4 import BeautifulSoup
import cchardet as chardet
from email.header import decode_header


@dataclass
class ImapConfig:
    """IMAP configuration dataclass."""

    host: str
    port: int
    user: str
    password: str
    mailbox: str = "INBOX"


class EmailProcessor:
    """Class to handle email processing operations."""

    # Constants
    MAX_WAIT: int = 300
    WAIT: int = 5
    TARGET_URL: str = "https://policemail.kcg.gov.tw/VerifyLetter.aspx"
    SUBJECT: str = "高雄市政府警察局警政信箱案件受理通知信"

    def __init__(self, config: ImapConfig):
        """Initialize with IMAP configuration."""
        self.config = config
        self.start_time = 0

    def process_email(self) -> None:
        """Verify the email first then delete the follow-up email."""
        self.start_time = time.time()
        status_print("Starting email processing...")

        with IMAPClient(self.config.host, self.config.port, ssl=True) as client:
            client.login(self.config.user, self.config.password)
            client.select_folder(self.config.mailbox)
            status_print(f"Connected to {self.config.host} as {self.config.user}")

            # Process verification emails
            self.search_and_process(client, ["BODY", self.TARGET_URL], "verification")

            # Process follow-up emails
            self.search_and_process(
                client, ["SUBJECT", self.SUBJECT], "follow-up", process_all=True
            )

        status_print(f"Processing completed in {time.time() - self.start_time:.1f}s")

    def search_and_process(
        self, client, search_criteria, description, process_all=False
    ):
        """Search for messages and process them."""
        elapsed = 0
        while elapsed < self.MAX_WAIT:
            status_print(f"Searching for {description} emails...")
            msgs = client.search(search_criteria, charset="UTF-8")

            if msgs:
                status_print(f"Found {len(msgs)} {description} message(s)")
                verified = [
                    msg_id for msg_id in msgs if self.process_message(msg_id, client)
                ]

                if verified:
                    status_print(f"Deleting {len(verified)} message(s)")
                    client.delete_messages(verified)
                    client.expunge()

                if not process_all:
                    break

            elapsed = time.time() - self.start_time
            if elapsed < self.MAX_WAIT:
                status_print(
                    f"Waiting {self.WAIT}s... ({int(self.MAX_WAIT - elapsed)}s remaining)"
                )
                with client.idle(timeout=self.WAIT) as idle:
                    idle.wait()

    def process_message(self, msg_id: int, client) -> bool:
        """Process a single message and return True if it was verified."""
        try:
            msg_data = client.fetch(msg_id, "RFC822")[msg_id][b"RFC822"]
            msg = email.message_from_bytes(msg_data)

            # Get decoded subject
            subject = self.decode_mail_header(msg.get("subject", ""))
            status_print(f"Processing: {subject or 'No subject'}")

            # Find and process HTML parts
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html = self.decode_content(part.get_payload(decode=True))
                    url = self.extract_verification_url(html)

                    if url:
                        status_print(f"Found URL: {url}")
                        try:
                            if requests.get(url, timeout=10).status_code == 200:
                                status_print("Verification successful")
                                return True
                        except requests.RequestException as e:
                            status_print(f"Request error: {e}")
            return False
        except Exception as e:
            status_print(f"Error processing message {msg_id}: {e}")
            return False

    @staticmethod
    def decode_mail_header(header: str) -> str:
        """Decode email header to readable text."""
        if not header:
            return ""
        return "".join(
            part.decode(enc or "utf-8") if isinstance(part, bytes) else part
            for part, enc in decode_header(header)
        )

    @staticmethod
    def decode_content(content: bytes) -> str:
        """Decode content with optimal encoding."""
        if not content:
            return ""

        # Try detected encoding first, then fallbacks
        encodings = [
            chardet.detect(content).get("encoding", "utf-8"),
            "utf-8",
            "big5",
            "gb18030",
            "gbk",
            "cp950",
        ]

        for enc in encodings:
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                pass

        return content.decode("utf-8", errors="replace")

    @classmethod
    def extract_verification_url(cls, html: str) -> Optional[str]:
        """Extract verification URL from HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=lambda href: href and cls.TARGET_URL in href)
        return links[0]["href"] if links else None


# Example configuration - in production, consider loading from environment or config file
CONFIG: ImapConfig = ImapConfig(
    host="disroot.org",
    port=993,
    user="anmicius@disroot.org",
    password="T9^hquUdfsr!$Yj^m5@RPL%q^aaFezM!qsvsKE6B8tc&!sJpfY",
)


def process_email() -> None:
    """Main function to process emails - maintains backward compatibility."""
    processor = EmailProcessor(CONFIG)
    processor.process_email()
