from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema.language_model import BaseLanguageModel
from autoppia_sdk.src.llms.interface import LLMServiceInterface

class OpenAIService(LLMServiceInterface):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        if not self._llm:
            self._llm = ChatOpenAI(model=self.model, api_key=self.api_key)
        return self._llm

    def update_model(self, model_name: str) -> None:
        self.model = model_name
        self._llm = None

    def update_api_key(self, api_key: str) -> None:
        self.api_key = api_key
        self._llm = None

class AnthropicService(LLMServiceInterface):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        if not self._llm:
            self._llm = ChatAnthropic(model=self.model, anthropic_api_key=self.api_key)
        return self._llm

    def update_model(self, model_name: str) -> None:
        self.model = model_name
        self._llm = None

    def update_api_key(self, api_key: str) -> None:
        self.api_key = api_key
        self._llm = None 