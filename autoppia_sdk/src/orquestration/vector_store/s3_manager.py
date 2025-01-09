import boto3
from django.conf import settings


class S3Manager:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def uploadFile(self, file_path, key):
        self.s3_client.upload_file(file_path, settings.AWS_STORAGE_BUCKET_NAME, key)

    def downloadFile(self, key, destination_path):
        self.s3_client.download_file(
            settings.AWS_STORAGE_BUCKET_NAME, key, destination_path
        )

    def createFolder(self, folder_name):
        self.s3_client.put_object(Bucket=settings.S3_BUCKET_NAME, Key=f"{folder_name}/")
