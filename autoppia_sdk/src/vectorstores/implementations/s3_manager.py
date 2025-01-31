import boto3
from dotenv import load_dotenv
import os
load_dotenv()


class S3Manager:
    """Manages S3 operations for file storage and retrieval.
    
    Handles uploading, downloading, and folder creation operations in AWS S3.
    Requires AWS credentials to be set in environment variables.
    """

    def __init__(self):
        """Initialize S3 client with credentials from environment variables."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    def uploadFile(self, file_path: str, key: str) -> None:
        """Upload a file to S3 bucket.
        
        Args:
            file_path (str): Local path to the file
            key (str): S3 object key (destination path in bucket)
        """
        self.s3_client.upload_file(file_path, os.getenv("AWS_STORAGE_BUCKET_NAME"), key)

    def downloadFile(self, key: str, destination_path: str) -> None:
        """Download a file from S3 bucket.
        
        Args:
            key (str): S3 object key to download
            destination_path (str): Local path where file should be saved
        """
        self.s3_client.download_file(
            os.getenv("AWS_STORAGE_BUCKET_NAME"), key, destination_path
        )

    def createFolder(self, folder_name: str) -> None:
        """Create a new folder in S3 bucket.
        
        Args:
            folder_name (str): Name of the folder to create
        """
        self.s3_client.put_object(Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"), Key=f"{folder_name}/")
