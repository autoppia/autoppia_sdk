import boto3
from dotenv import load_dotenv
import os
load_dotenv()


class S3Manager:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    def uploadFile(self, file_path, key):
        self.s3_client.upload_file(file_path, os.getenv("AWS_STORAGE_BUCKET_NAME"), key)

    def downloadFile(self, key, destination_path):
        self.s3_client.download_file(
            os.getenv("AWS_STORAGE_BUCKET_NAME"), key, destination_path
        )

    def createFolder(self, folder_name):
        self.s3_client.put_object(Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"), Key=f"{folder_name}/")
