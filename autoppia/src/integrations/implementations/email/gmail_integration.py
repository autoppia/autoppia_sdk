import base64
import json
import os
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from autoppia.src.integrations.implementations.email.interface import EmailIntegration
from autoppia.src.integrations.config import IntegrationConfig
from autoppia.src.integrations.implementations.base import Integration


class GmailIntegration(EmailIntegration, Integration):
    """Gmail-specific email integration using Gmail API for sending and receiving emails.

    This class implements email functionality using Gmail's REST API.
    It supports both regular Gmail accounts and Google Workspace accounts.

    Required Configuration Attributes:
        client_id (str): Gmail API OAuth2 Client ID
        client_secret (str): Gmail API OAuth2 Client Secret
        refresh_token (str): Gmail API OAuth2 Refresh Token
        user_email (str): Gmail account email address

    Optional Configuration Attributes:
        access_token (str): Gmail API OAuth2 Access Token (auto-generated)
        scopes (str): Comma-separated Gmail API OAuth2 Scopes
        api_version (str): Gmail API version to use (default: v1)

    Attributes:
        integration_config (IntegrationConfig): Configuration object containing Gmail settings
        service: Gmail API service object
        SCOPES: Gmail API scopes for read and send permissions
    """

    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
              'https://www.googleapis.com/auth/gmail.send']

    def __init__(self, integration_config: IntegrationConfig):
        self.integration_config = integration_config
        
        # Get OAuth2 credentials from config
        self.client_id = integration_config.attributes.get("client_id")
        self.client_secret = integration_config.attributes.get("client_secret")
        self.refresh_token = integration_config.attributes.get("refresh_token")
        self.access_token = integration_config.attributes.get("access_token")
        self.scopes = integration_config.attributes.get("scopes", "").split(",") if integration_config.attributes.get("scopes") else self.SCOPES
        self.user_email = integration_config.attributes.get("user_email")
        self.api_version = integration_config.attributes.get("api_version", "v1")
        
        # Validate required fields
        if not self.client_id:
            raise ValueError("Gmail client_id is required")
        if not self.client_secret:
            raise ValueError("Gmail client_secret is required")
        if not self.refresh_token:
            raise ValueError("Gmail refresh_token is required")
        if not self.user_email:
            raise ValueError("Gmail user_email is required")
        
        # Initialize Gmail service
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Initialize and return Gmail API service."""
        creds = None
        
        # Create credentials from individual OAuth2 attributes
        try:
            # If we have an access token, try to use it first
            if self.access_token:
                creds = Credentials(
                    token=self.access_token,
                    refresh_token=self.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    scopes=self.scopes
                )
            else:
                # Create credentials with just refresh token
                creds = Credentials(
                    token=None,
                    refresh_token=self.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    scopes=self.scopes
                )
            
            # Check if credentials are valid, refresh if needed
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # Update access token in config if it was refreshed
                    self._update_access_token(creds.token)
                else:
                    raise ValueError("Invalid Gmail credentials - refresh token may be expired")
                    
        except Exception as e:
            raise ValueError(f"Error setting up Gmail authentication: {e}")
        
        return build('gmail', self.api_version, credentials=creds)
    
    def _update_access_token(self, new_access_token: str):
        """Update the access token in the integration config."""
        try:
            # Update the access token in the integration config
            if hasattr(self.integration_config, 'attributes'):
                self.integration_config.attributes['access_token'] = new_access_token
        except Exception as e:
            print(f"Warning: Could not update access token: {e}")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str = None,
        files: List[str] = None,
    ) -> Optional[str]:
        """Send an email using Gmail API.

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
            # Create email message
            message = self._create_message(to, subject, body, html_body, files)
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            content_snippet = (html_body or body)[:50]
            return f"Gmail email sent successfully to {to}. Message ID: {sent_message['id']}. Content preview: '{content_snippet}'"
            
        except HttpError as error:
            print(f"Gmail API send error: {error}")
            return None
        except Exception as e:
            print(f"Gmail send error: {e}")
            return None

    def _create_message(self, to: str, subject: str, body: str, html_body: str = None, files: List[str] = None):
        """Create a message for Gmail API."""
        import email
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        # Add body
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        else:
            message.attach(MIMEText(body, 'plain'))

        # Add attachments
        if files:
            for file_path in files:
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {file_path.split("/")[-1]}'
                )
                message.attach(part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def read_emails(self, num: int = 5) -> Optional[List[Dict[str, str]]]:
        """Read recent emails from Gmail using Gmail API.

        Args:
            num (int, optional): Number of recent emails to retrieve. Defaults to 5.

        Returns:
            Optional[List[Dict[str, str]]]: List of dictionaries containing email data
                                          (From, Subject, Body) if successful,
                                          None if an error occurred
        """
        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me', maxResults=num
            ).execute()
            
            messages = results.get('messages', [])
            emails_list = []

            for message in messages:
                # Get message details
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()
                
                # Extract headers
                headers = msg['payload'].get('headers', [])
                email_data = {
                    "From": "",
                    "Subject": "",
                    "Body": "",
                    "MessageId": message['id']
                }
                
                # Extract From and Subject from headers
                for header in headers:
                    if header['name'] == 'From':
                        email_data["From"] = header['value']
                    elif header['name'] == 'Subject':
                        email_data["Subject"] = header['value']
                
                # Extract body
                email_data["Body"] = self._extract_body(msg['payload'])
                
                emails_list.append(email_data)

            return emails_list

        except HttpError as error:
            print(f"Gmail API read error: {error}")
            return None
        except Exception as e:
            print(f"Gmail read error: {e}")
            return None

    def _extract_body(self, payload):
        """Extract email body from Gmail API payload."""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')
        
        return body

    def read_emails_by_label(self, label: str = "INBOX", num: int = 5) -> Optional[List[Dict[str, str]]]:
        """Read recent emails from a specific Gmail label using Gmail API.

        Args:
            label (str, optional): Gmail label to read from. Defaults to "INBOX".
            num (int, optional): Number of recent emails to retrieve. Defaults to 5.

        Returns:
            Optional[List[Dict[str, str]]]: List of dictionaries containing email data
                                          (From, Subject, Body) if successful,
                                          None if an error occurred
        """
        try:
            # Get list of messages with specific label
            query = f"label:{label}"
            results = self.service.users().messages().list(
                userId='me', maxResults=num, q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails_list = []

            for message in messages:
                # Get message details
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()
                
                # Extract headers
                headers = msg['payload'].get('headers', [])
                email_data = {
                    "From": "",
                    "Subject": "",
                    "Body": "",
                    "MessageId": message['id'],
                    "Label": label
                }
                
                # Extract From and Subject from headers
                for header in headers:
                    if header['name'] == 'From':
                        email_data["From"] = header['value']
                    elif header['name'] == 'Subject':
                        email_data["Subject"] = header['value']
                
                # Extract body
                email_data["Body"] = self._extract_body(msg['payload'])
                
                emails_list.append(email_data)

            return emails_list

        except HttpError as error:
            print(f"Gmail API read by label error: {error}")
            return None
        except Exception as e:
            print(f"Gmail read by label error: {e}")
            return None

    def get_gmail_labels(self) -> Optional[List[str]]:
        """Get all available Gmail labels using Gmail API.

        Returns:
            Optional[List[str]]: List of Gmail labels if successful, None if an error occurred
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            label_list = []
            for label in labels:
                label_list.append(label['name'])
            
            return label_list

        except HttpError as error:
            print(f"Gmail API get labels error: {error}")
            return None
        except Exception as e:
            print(f"Gmail get labels error: {e}")
            return None
