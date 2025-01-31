from autoppia_backend_client.models import UserLLMModel
from autoppia_sdk.src.llms.implementations.openai_service import OpenAIService
from autoppia_sdk.src.llms.implementations.anthropic_service import AnthropicService

class LLMAdapter:
    def __init__(self, llm_dto):
        self.llm_dto: UserLLMModel = llm_dto

    def from_backend(self):
        """Initialize LLM service from backend configuration.
        
        Returns:
            Initialized LLM service instance or None for unsupported providers
            
        Raises:
            ValueError: For missing required API keys
        """
        provider_type = self.llm_dto.llm_model.provider.provider_type.upper()
        api_key = self.llm_dto.api_key
        model_name = self.llm_dto.llm_model.name.lower()

        if not api_key:
            raise ValueError(f"Missing API key for {provider_type} provider")

        if provider_type == "OPENAI":
            return OpenAIService(api_key=api_key, model=model_name)
        elif provider_type == "ANTHROPIC":
            return AnthropicService(api_key=api_key, model=model_name)
        
        return None
