from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO

from autoppia_sdk.src.vectorstores.implementations.pinecone_manager import PineconeManager
from autoppia_sdk.src.vectorstores.implementations.openai_manager import OpenAIManager


class VectorStoreAdapter:
    def __init__(self, vector_store_dto):
        self.vector_store_dto: VectorStoreDTO = vector_store_dto

    def from_backend(self):
        provider = self.vector_store_dto.provider
        if provider == "OPENAI":
            return OpenAIManager(
                index_name=self.vector_store_dto.index_name, 
                vector_store_id=self.vector_store_dto.openai_vector_store_id
            )
        elif provider == "PINECONE":
            return PineconeManager(
                api_key=self.vector_store_dto.api_key,
                index_name=self.vector_store_dto.index_name
            )
        return None
