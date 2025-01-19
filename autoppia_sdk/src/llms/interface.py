from abc import ABC, abstractmethod
from langchain.schema.language_model import BaseLanguageModel


class LLMServiceInterface(ABC):
    @abstractmethod
    def get_llm(self) -> BaseLanguageModel:
        """Get the language model instance"""
        pass

    @abstractmethod
    def update_model(self, model_name: str) -> None:
        """Update the model name"""
        pass

    @abstractmethod
    def update_api_key(self, api_key: str) -> None:
        """Update the API key"""
        pass
