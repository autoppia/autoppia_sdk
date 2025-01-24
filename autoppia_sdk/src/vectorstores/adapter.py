from typing import Union
from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO
from autoppia_sdk.src.vectorstores.implementations.pinecone_manager import PineconeManager
from autoppia_sdk.src.vectorstores.implementations.openai_manager import OpenAIManager


class VectorStoreAdapter:
    """Adapter for creating vector store manager instances based on backend configuration.
    
    Handles provider-specific initialization and credential validation.
    
    Args:
        vector_store_dto (VectorStoreDTO): Configuration data from backend
    """
    
    def __init__(self, vector_store_dto: VectorStoreDTO):
        self.vector_store_dto = vector_store_dto
        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """Validate required credentials for the configured provider."""
        provider = self.vector_store_dto.provider.upper()
        if provider == "PINECONE" and not self.vector_store_dto.api_key:
            raise ValueError("Pinecone configuration requires: API key")
        if provider == "OPENAI" and not self.vector_store_dto.openai_vector_store_id:
            raise ValueError("OpenAI configuration requires: Vector Store ID")

    def from_backend(self) -> Union[OpenAIManager, PineconeManager, None]:
        """Create a vector store manager instance based on configured provider.
        
        Returns:
            Union[OpenAIManager, PineconeManager]: Initialized vector store manager
            None: If provider is not supported
            
        Raises:
            ValueError: For missing required configuration parameters
        """
        match self.vector_store_dto.provider:
            case "OPENAI":
                return OpenAIManager(
                    index_name=self.vector_store_dto.index_name,
                    vector_store_id=self.vector_store_dto.openai_vector_store_id
                )
            case "PINECONE":
                return PineconeManager(
                    api_key=self.vector_store_dto.api_key,
                    index_name=self.vector_store_dto.index_name
                )
            case _:
                raise ValueError(f"Unsupported vector store provider: {self.vector_store_dto.provider}")
