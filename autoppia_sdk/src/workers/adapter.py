from typing import List

from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO
from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO
from autoppia_backend_client.models import UserLLMModel as UserLLMModelDTO
from autoppia_backend_client.models import Worker as WorkerDTO

from autoppia_sdk.src.vectorstores.adapter import VectorStoreAdapter
from autoppia_sdk.src.toolkits.adapter import UserToolkitAdapter
from autoppia_sdk.src.workers.worker_user_conf_service import WorkerUserConfService
from autoppia_sdk.src.toolkits.interface import UserToolkit

from typing import Dict, Any, Optional
from dataclasses import dataclass

class AIWorkerAdapter:
    def __init__(self, worker_id=None, worker_dto=None):
        self.worker_service = WorkerUserConfService()
        if worker_dto:
            self.worker_dto: WorkerDTO = worker_dto
        elif worker_id:
            self.worker_dto: WorkerDTO = self.worker_service.retrieveWorker(
                worker_id=worker_id
            )

        self.vector_store_dto: VectorStoreDTO = self.worker_dto.embedding_database
        self.user_toolkits_dto: List[
            UserToolkitDTO
        ] = self.worker_dto.user_configuration
        self.user_llm_dto: UserLLMModelDTO = self.worker_dto.user_llm_model
        self.user_toolkits: List[UserToolkit] = []
        self.user_llm: str = ""
        self.agent = self.worker_dto.agent
        self.instruction = (
            self.worker_dto.system_prompt.prompt
            if self.worker_dto.system_prompt
            else ""
        )

    def from_backend(self):
        self.vector_store = VectorStoreAdapter(self.vector_store_dto).from_backend()

        for user_configuration in self.worker_dto.user_configuration:
            user_toolkit = UserToolkitAdapter(user_configuration).from_backend()
            self.user_toolkits.append(user_toolkit)

        self.user_llm = self.user_llm_dto.llm_model.name

        return (
            self.user_llm,
            self.vector_store,
            self.user_toolkits,
            self.agent,
            self.instruction,
        )

@dataclass
class IntegrationConfig:
    name: str
    category: str
    attributes: Dict[str, Any]

class WorkerConfigAdapter:
    def __init__(self, worker_data):
        self.worker_data = worker_data
        self.template = getattr(worker_data, 'template', {})
        self.user_integrations = getattr(worker_data, 'user_integration', [])
        
    def get_integration_by_category(self, category: str) -> Optional[IntegrationConfig]:
        """Extract integration configuration by category."""
        for integration in self.user_integrations:
            if category in integration.integration_obj.category:
                attributes = {}
                for attr in integration.user_integration_attributes:
                    name = attr.integration_attribute_obj.name
                    # Handle both credential and regular values
                    if attr.credential_obj:
                        value = attr.credential_obj.credential
                    else:
                        value = attr.value
                    attributes[name] = value
                
                return IntegrationConfig(
                    name=integration.name,
                    category=integration.integration_obj.category,
                    attributes=attributes
                )
        return None

    def get_worker_metadata(self) -> Dict[str, Any]:
        """Extract worker metadata."""
        return {
            "id": getattr(self.worker_data, 'id', None),
            "name": getattr(self.worker_data, 'name', None),
            "description": getattr(self.template, 'description', None),
            "category": getattr(self.template, 'integration_category', None),
            "state": getattr(self.worker_data, 'state', False)
        }

    def get_system_prompt(self) -> Optional[Dict[str, Any]]:
        """Extract system prompt configuration."""
        prompt_data = getattr(self.worker_data, 'system_prompt', None)
        if prompt_data:
            return {
                "name": getattr(prompt_data, 'name', None),
                "category": getattr(getattr(prompt_data, 'category', {}), 'name', None),
                "prompt": getattr(prompt_data, 'prompt', None)
            }
        return None

    def to_worker_config(self) -> Dict[str, Any]:
        """Convert all configurations to worker format."""
        config = {
            "metadata": self.get_worker_metadata(),
            "system_prompt": self.get_system_prompt()
        }
        
        # Add all integrations found in the worker data
        integrations = {}
        for integration in self.user_integrations:
            category = integration.integration_obj.category
            integration_config = self.get_integration_by_category(category)
            if integration_config:
                integrations[category] = integration_config.attributes
        
        config["integrations"] = integrations
        return config
    