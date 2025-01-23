from typing import List

from autoppia_backend_client.models import EmbeddingDatabase as VectorStoreDTO
from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO
from autoppia_backend_client.models import UserLLMModel as UserLLMModelDTO
from autoppia_backend_client.models import Worker as WorkerDTO
from autoppia_sdk.src.workers.worker_user_conf_service import WorkerUserConfService
from autoppia_sdk.src.integrations.adapter import IntegrationsAdapter
from autoppia_sdk.src.vectorstores.adapter import VectorStoreAdapter
from autoppia_sdk.src.llms.adapter import LLMAdapter
from autoppia_sdk.src.workers.interface import WorkerConfig

class AIWorkerConfigAdapter:
    def __init__(self, worker_id=None):
        self.worker_id = worker_id

    def adapt_integrations(self):
        return IntegrationsAdapter().from_autoppia_backend(self.worker_config_dtao)

    def adapt_vector_stores(self):
        if self.worker_config_dtao.embedding_database:
            vector_store = VectorStoreAdapter(self.worker_config_dtao.embedding_database).from_backend()
            provider = self.worker_config_dtao.embedding_database.provider
            return {provider: vector_store} if vector_store else {}
        return {}

    def adapt_llms(self):
        if self.worker_config_dtao.user_llm_model:
            llm = LLMAdapter(self.worker_config_dtao.user_llm_model).from_backend()
            provider = self.worker_config_dtao.user_llm_model.llm_model.provider.provider_type.lower()
            return {provider: llm} if llm else {}
        return {}

    def adapt_toolkits(self):
        raise Exception("We are not using this YET. do not implement yet.")

    def from_autoppia_user_backend(self, worker_config_dtao):
        self.worker_config_dtao = worker_config_dtao
        integrations = self.adapt_integrations()
        vector_stores = self.adapt_vector_stores()
        llms = self.adapt_llms()
        
        worker_config = WorkerConfig(
            integrations=integrations,
            vectorstores=vector_stores,
            llms=llms,
            system_prompt=worker_config_dtao.system_prompt.prompt if worker_config_dtao.system_prompt else None,
            name=worker_config_dtao.name
        )
        return worker_config
