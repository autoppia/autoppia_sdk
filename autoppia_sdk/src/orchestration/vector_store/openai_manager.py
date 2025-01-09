from openai import OpenAI

from autoppia_sdk.src.standardization.vector_store.interface import VectorStoreWrapper
from autoppia_sdk.src.orchestration.vector_store.s3_manager import S3Manager


class OpenaiManager(VectorStoreWrapper):
    def __init__(self, index_name: str, vector_store_id: str = None):
        self.vector_store_id = vector_store_id
        self.client = OpenAI()
        self.s3_manager = S3Manager()
        self.index_name = index_name

    def get_or_create_collection(self):
        if self.vector_store_id:
            vector_store = self.client.beta.vector_stores.retrieve(
                vector_store_id=self.vector_store_id
            )
            return vector_store
        else:
            return self.client.beta.vector_stores.create(name=self.index_name)

    def add_document(self, file_id):
        self.client.beta.vector_stores.files.create(
            vector_store_id=self.vector_store_id, file_id=file_id
        )

    def get_context(self):
        pass

    def get_files(self, vector_store_id):
        vector_store_files = self.client.beta.vector_stores.files.list(
            vector_store_id=vector_store_id
        )

        return vector_store_files

    def add_file_batch(self, vector_store_id, file_ids):
        self.client.beta.vector_stores.file_batches.create(
            vector_store_id=vector_store_id, file_ids=file_ids
        )
