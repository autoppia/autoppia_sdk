import email
import imaplib
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from autoppia.src.integrations.implementations.email.interface import EmailIntegration
from autoppia.src.integrations.config import IntegrationConfig
from autoppia.src.integrations.implementations.base import Integration


class SMPTEmailIntegration(EmailIntegration, Integration):
    """SMTP-based email integration for sending and receiving emails.

    This class implements email functionality using SMTP for sending emails
    and IMAP for receiving emails. It requires configuration for both SMTP
    and IMAP servers.

    Attributes:
        integration_config (IntegrationConfig): Configuration object containing email settings
        smtp_server (str): SMTP server hostname
        smtp_port (int): SMTP server port
        imap_server (str): IMAP server hostname
        imap_port (int): IMAP server port
        email (str): Email address used for authentication
        _password (str): Password used for authentication
    """

    def __init__(self, integration_config: IntegrationConfig):
        self.integration_config = integration_config
        self.smtp_server = integration_config.attributes.get("SMTP Server")
        self.smtp_port = integration_config.attributes.get("SMTP Port")
        self.imap_server = integration_config.attributes.get("IMAP Server")
        self.imap_port = integration_config.attributes.get("IMAP Port")
        self.email = integration_config.attributes.get("email")
        self._password = integration_config.attributes.get("password")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str = None,
        files: List[str] = None,
    ) -> Optional[str]:
        """Send an email using configured SMTP settings.

        Args:
            to (str): Recipient email address
            subject (str): Email subject line
            body (str): Plain text email body
            html_body (str, optional): HTML formatted email body. Defaults to None.
            files (List[str], optional): List of file paths to attach. Defaults to None.

        Returns:
            Optional[str]: Success message with email details if sent successfully,
                         None if an error occurred
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
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
            server.login(self.email, self._password)
            server.send_message(msg)
            server.quit()

            content_snippet = (html_body or body)[:50]
            return f"Email sent successfully from {self.email} to {to}. Message content preview: '{content_snippet}'"
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def read_emails(self, num: int = 5) -> Optional[List[Dict[str, str]]]:
        """Read recent emails from the IMAP inbox.

        Args:
            num (int, optional): Number of recent emails to retrieve. Defaults to 5.

        Returns:
            Optional[List[Dict[str, str]]]: List of dictionaries containing email data
                                          (From, Subject, Body) if successful,
                                          None if an error occurred
        """
        imap_conn = None
        try:
            imap_conn = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            imap_conn.login(self.email, self._password)
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
                            email_data["Body"] = part.get_payload(
                                decode=True).decode()
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
