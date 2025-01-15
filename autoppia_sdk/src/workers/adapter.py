from typing import List

from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO
from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO
from autoppia_backend_client.models import UserLLMModel as UserLLMModelDTO
from autoppia_backend_client.models import Worker as WorkerDTO

from autoppia_sdk.src.orchestration.vectorstores.adapter import VectorStoreAdapter
from autoppia_sdk.src.orchestration.toolkits.adapter import UserToolkitAdapter
from autoppia_sdk.src.orchestration.workers.infrastructure.service import WorkerService




class AIWorkerAdapter:
    def __init__(self, worker_id=None, worker_dto=None):
        self.worker_service = WorkerService()
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

    def create_worker_from_id(worker_id: str) -> AIWorker:
        # 1. Use AIWorkerAdapter to fetch the WorkerDTO from backend
        # 2. Parse the worker type or module/class name
        # 3. Dynamically import the worker’s Python class 
        #    (or if you already pip installed, you can do import)
        # 4. Initialize the worker with the merged config
        return MyWorker(...)