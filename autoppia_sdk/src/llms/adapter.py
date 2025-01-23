from autoppia_backend_client.models import UserLLMModel
from autoppia_sdk.src.llms.implementations.openai_service import OpenAIService
from autoppia_sdk.src.llms.implementations.anthropic_service import AnthropicService

class LLMAdapter:
    def __init__(self, llm_dto):
        self.llm_dto: UserLLMModel = llm_dto

    def from_backend(self):
        provider_type = self.llm_dto.llm_model.provider.provider_type
        api_key = self.llm_dto.api_key
        model_name = self.llm_dto.llm_model.name

        if provider_type == "OPENAI":
            return OpenAIService(api_key=api_key, model=model_name)
        elif provider_type == "ANTHROPIC":
            return AnthropicService(api_key=api_key, model=model_name)
        else:
            return None
