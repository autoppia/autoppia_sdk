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

    Attributes:
        integration_config (IntegrationConfig): Configuration object containing Gmail settings
        service: Gmail API service object
        credentials: Google OAuth2 credentials
        SCOPES: Gmail API scopes for read and send permissions
    """

    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
              'https://www.googleapis.com/auth/gmail.send']

    def __init__(self, integration_config: IntegrationConfig):
        self.integration_config = integration_config
        
        # Get credentials from config
        self.credentials_json = integration_config.attributes.get("credentials_json")
        self.token_json = integration_config.attributes.get("token_json")
        
        # Validate required fields
        if not self.credentials_json:
            raise ValueError("Gmail credentials_json is required")
        
        # Initialize Gmail service
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Initialize and return Gmail API service."""
        creds = None
        
        # Load existing token if available
        if self.token_json:
            try:
                token_data = json.loads(self.token_json)
                creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    credentials_data = json.loads(self.credentials_json)
                    flow = InstalledAppFlow.from_client_config(credentials_data, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise ValueError(f"Error setting up Gmail authentication: {e}")
        
        # Save the credentials for the next run
        if self.token_json is None:
            # Store token for future use
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            # Note: In a real implementation, you'd want to save this back to the config
        
        return build('gmail', 'v1', credentials=creds)

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
