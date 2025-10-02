from typing import Optional, Dict, Any
from autoppia_backend_client.models import WorkerConfig as WorkerConfigDTO
from autoppia.src.integrations.adapter import IntegrationsAdapter
from autoppia.src.vectorstores.adapter import VectorStoreAdapter
from autoppia.src.llms.adapter import LLMAdapter
from autoppia.src.workers.interface import WorkerConfig


class AIWorkerConfigAdapter:
    """Adapter for constructing worker configurations from backend DTOs.
    
    Handles conversion of backend data transfer objects into domain-specific
    configuration models with proper validation and resource management.
    
    Args:
        worker_id: Optional identifier for worker instance tracking
    """
    
    def __init__(self, worker_id: Optional[str] = None) -> None:
        self.worker_id = worker_id
        self.worker_config_dto: Optional[WorkerConfigDTO] = None


    def adapt_integrations(self) -> Dict[str, Any]:
        """Adapt integrations configuration from backend DTO.
        
        Returns:
            Dictionary of initialized integration clients keyed by provider
            
        Raises:
            ValueError: If required integration configuration is missing
        """
        if not self.worker_config_dto:
            raise ValueError("Configuration DTO not loaded")
        return IntegrationsAdapter().from_autoppia_backend(self.worker_config_dto)

    def adapt_vector_stores(self) -> Dict[str, Any]:
        """Adapt vector store configuration from backend DTO.
        
        Returns:
            Dictionary of vector store clients keyed by provider
        """
        if not self.worker_config_dto or not self.worker_config_dto.embedding_database:
            return None

        return VectorStoreAdapter(
            self.worker_config_dto.embedding_database
        ).from_backend()
        
    def adapt_llms(self) -> Dict[str, Any]:
        """Adapt LLM configuration from backend DTO.
        
        Returns:
            Dictionary of LLM clients keyed by provider
        """
        if not self.worker_config_dto or not self.worker_config_dto.user_llm_model:
            return None

        return LLMAdapter(self.worker_config_dto.user_llm_model).from_backend()

    def adapt_toolkits(self) -> None:
        """Placeholder for toolkit adaptation (not implemented)."""
        raise NotImplementedError("Toolkit adaptation not yet implemented")

    def from_autoppia_user_backend(self, worker_config_dto: WorkerConfigDTO) -> WorkerConfig:
        """Construct worker configuration from backend DTO with validation.
        
        Args:
            worker_config_dto: Source data transfer object from backend
            
        Returns:
            WorkerConfig: Initialized worker configuration with integrated services
            
        Raises:
            ValueError: For missing required fields or invalid configurations
            RuntimeError: If service initialization fails
        """
        self.worker_config_dto = worker_config_dto
        
        if not worker_config_dto.name:
            raise ValueError("Missing required field: 'name' (worker identifier)")

        return WorkerConfig(
            llm=self.adapt_llms(),
            vectorstore=self.adapt_vector_stores(),
            integrations=self.adapt_integrations(),
            system_prompt=worker_config_dto.system_prompt.prompt if worker_config_dto.system_prompt else None,
            mcp=worker_config_dto.mcp if worker_config_dto.mcp else None,
            name=worker_config_dto.name,
            ip=worker_config_dto.ip,
            port=worker_config_dto.port,
            template_id=worker_config_dto.template_id
        )
