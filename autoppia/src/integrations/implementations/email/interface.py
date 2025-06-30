from abc import ABC, abstractmethod
from typing import List, Optional, Dict


class EmailIntegration(ABC):
    @abstractmethod
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        files: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Sends an email to the specified recipient.

        Args:
            to (str): Recipient's email address.
            subject (str): Subject of the email.
            body (str): Plain text body of the email.
            html_body (Optional[str]): HTML version of the email body. Defaults to None.
            files (Optional[List[str]]): List of file paths to attach. Defaults to None.

        Returns:
            Optional[str]: The result of the operation, such as a message ID, or None if not applicable.
        """
        pass

    @abstractmethod
    def read_emails(self, num: int = 5) -> Optional[List[Dict[str, str]]]:
        """
        Reads a specified number of emails.

        Args:
            num (int): Number of emails to read. Defaults to 5.

        Returns:
            Optional[List[Dict[str, str]]]: A list of email details represented as dictionaries, or None if no emails are retrieved.
        """
        pass
