from typing import List

from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO
from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO
from autoppia_backend_client.models import UserLLMModel as UserLLMModelDTO
from autoppia_backend_client.models import Worker as WorkerDTO

from autoppia_agentic_framework.src.documents.application.VectorStoreAdapter import VectorStoreAdapter
from autoppia_agentic_framework.src.tools.application.UserToolkitAdapter import UserToolkitAdapter
from autoppia_agentic_framework.src.workers.domain.classes import UserToolkit
from autoppia_agentic_framework.src.workers.infrastructure.service import WorkerService
from autoppia_sdk.src.standarization.llm.domain.interfaces import LLMService
from autoppia_sdk.src.standarization.vector_store.domain.interfaces import VectorStore


class AIWorkerAdapter:
    def __init__(self, worker_id=None, worker_dto=None, llm_service: LLMService = None, vector_store: VectorStore = None):
        self.worker_service = WorkerService()
        self.llm_service = llm_service
        self.vector_store = vector_store
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
        if not self.vector_store:
            self.vector_store = VectorStoreAdapter(self.vector_store_dto).from_backend()

        for user_configuration in self.worker_dto.user_configuration:
            user_toolkit = UserToolkitAdapter(user_configuration).from_backend()
            self.user_toolkits.append(user_toolkit)

        if not self.llm_service:
            self.user_llm = self.user_llm_dto.llm_model.name
        else:
            self.user_llm = self.llm_service

        return (
            self.user_llm,
            self.vector_store,
            self.user_toolkits,
            self.agent,
            self.instruction,
        )
