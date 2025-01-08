from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO

from autoppia_agentic_framework.src.documents.infrastructure.pinecone_manager import PineconeManager


class VectorStoreAdapter:
    def __init__(self, vector_store_dto):
        self.vector_store_dto: VectorStoreDTO = vector_store_dto

    def from_backend(self):
        provider = self.vector_store_dto.provider
        if provider == "OPENAI":
            return self.vector_store_dto.openai_vector_store_id

        elif provider == "PINECONE":
            api_key = self.vector_store_dto.api_key
            index_name = self.vector_store_dto.index_name
            return PineconeManager(api_key=api_key, index_name=index_name)
