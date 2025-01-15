import email
import imaplib
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from autoppia_sdk.src.integrations.interfaces import Integration


class EmailIntegration(Integration):
    def __init__(self):
        self.smtp_server: Optional[str] = None
        self.smtp_port: Optional[int] = None
        self.imap_server: Optional[str] = None
        self.imap_port: Optional[int] = None
        self.username: Optional[str] = None
        self._password: Optional[str] = None

    def configure(self, user_config: Dict[str, Any]) -> None:
        """Configure email settings from user configuration"""
        self.smtp_server = user_config["smtp_server"]
        self.smtp_port = user_config["smtp_port"]
        self.imap_server = user_config["imap_server"]
        self.imap_port = user_config["imap_port"]
        self.username = user_config["username"]
        self._password = user_config["password"]

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str = None,
        files: List[str] = None,
    ) -> Optional[str]:
        """Send an email using configured settings"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to
            msg["Subject"] = subject

            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            if files:
                for file in files:
                    part = MIMEBase("application", "octet-stream")
                    with open(file, "rb") as f:
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={file.split('/')[-1]}",
                    )
                    msg.attach(part)

            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.username, self._password)
            server.send_message(msg)
            server.quit()

            content_snippet = (html_body or body)[:50]
            return f"Email sent successfully from {self.username} to {to}. Message content preview: '{content_snippet}'"
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def read_emails(self, num: int = 5) -> Optional[List[Dict[str, str]]]:
        """Read emails using configured settings"""
        imap_conn = None
        try:
            imap_conn = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            imap_conn.login(self.username, self._password)
            imap_conn.select("inbox")

            _, message_numbers = imap_conn.search(None, "ALL")
            start_index = max(0, len(message_numbers[0].split()) - num)
            emails_list = []

            for num in message_numbers[0].split()[start_index:]:
                _, data = imap_conn.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])

                email_data = {
                    "From": msg["From"],
                    "Subject": msg["Subject"],
                    "Body": "",
                }

                if msg.is_multipart():
                    for part in msg.walk():
                        if (
                            part.get_content_type() == "text/plain"
                            and "attachment" not in str(part.get("Content-Disposition"))
                        ):
                            email_data["Body"] = part.get_payload(decode=True).decode()
                            break
                else:
                    email_data["Body"] = (
                        msg.get_payload(decode=True).decode()
                        if msg.get_payload()
                        else ""
                    )

                emails_list.append(email_data)

            return emails_list

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if imap_conn:
                try:
                    imap_conn.logout()
                except Exception as e:
                    print(f"Error during logout: {e}")
