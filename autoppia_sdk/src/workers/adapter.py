from typing import List

from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO
from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO
from autoppia_backend_client.models import UserLLMModel as UserLLMModelDTO
from autoppia_backend_client.models import Worker as WorkerDTO
from autoppia_sdk.src.workers.worker_user_conf_service import WorkerUserConfService
from autoppia_sdk.src.integrations.adapter import IntegrationsAdapter
from autoppia_sdk.src.workers.interface import WorkerConfig


class AIWorkerConfigAdapter:
    def __init__(self, worker_id=None):
        self.worker_id = worker_id

    def adapt_integrations(self):
        self.integrations = IntegrationsAdapter().from_autoppia_backend(self.worker_config_dtao)

    def adapt_vector_stores(self):
        pass
        # self.vector_store = VectorStoreAdapter(self.vector_store_dto).from_backend()

    def adapt_llms(self):
        pass
        # self.user_llm = self.user_llm_dto.llm_model.name

    def adapt_toolkits(self):
        raise Exception("We are not using this YET. do not implement yet.")

    def from_autoppia_user_backend(self, worker_config_dtao):
        self.worker_config_dtao = worker_config_dtao
        integrations = self.adapt_integrations()
        worker_config = WorkerConfig(integrations=integrations)
        return worker_config
