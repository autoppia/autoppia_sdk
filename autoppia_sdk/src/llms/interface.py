from abc import ABC, abstractmethod
from langchain.schema.language_model import BaseLanguageModel


class LLMServiceInterface(ABC):
    """Interface for language model services.
    
    This abstract base class defines the required interface that all
    language model service implementations must follow.
    """

    @abstractmethod
    def get_llm(self) -> BaseLanguageModel:
        """Get the language model instance.
        
        Returns:
            BaseLanguageModel: The configured language model instance
        """
        pass

    @abstractmethod
    def update_model(self, model_name: str) -> None:
        """Update the model name.
        
        Args:
            model_name (str): New model name to use
        """
        pass

    @abstractmethod
    def update_api_key(self, api_key: str) -> None:
        """Update the API key.
        
        Args:
            api_key (str): New API key to use
        """
        pass
