from autoppia_backend_client.models import UserLLMModel
from autoppia.src.llms.implementations.openai_service import OpenAIService
from autoppia.src.llms.implementations.anthropic_service import AnthropicService

class LLMAdapter:
    """Adapter for initializing LLM services from backend configuration.
    
    This class handles the conversion of backend LLM configuration into
    appropriate LLM service instances.
    
    Attributes:
        llm_dto (UserLLMModel): Data transfer object containing LLM configuration
    """

    def __init__(self, llm_dto):
        """Initialize the LLM adapter.
        
        Args:
            llm_dto (UserLLMModel): Backend LLM configuration
        """
        self.llm_dto: UserLLMModel = llm_dto

    def from_backend(self):
        """Initialize LLM service from backend configuration.
        
        Returns:
            LLMServiceInterface: Initialized LLM service instance
            None: For unsupported providers
            
        Raises:
            ValueError: If required API key is missing
        """
        provider_type = self.llm_dto.llm_model.provider.provider_type.upper()
        api_key = self.llm_dto.api_key.credential
        model_name = self.llm_dto.llm_model.name.lower()

        if not api_key:
            raise ValueError(f"Missing API key for {provider_type} provider")

        if provider_type == "OPENAI":
            return OpenAIService(api_key=api_key, model=model_name)
        elif provider_type == "ANTHROPIC":
            return AnthropicService(api_key=api_key, model=model_name)
        
        return None
