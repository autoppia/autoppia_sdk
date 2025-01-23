from langchain_anthropic import ChatAnthropic
from autoppia_sdk.src.llms.interface import LLMServiceInterface

class AnthropicService(LLMServiceInterface):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self):
        if not self._llm:
            self._llm = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model=self.model,
                max_tokens=4096  # Optional: configure max output tokens
            )
        return self._llm

    def update_model(self, model_name: str):
        self.model = model_name
        self._llm = None  # Force recreation with new model

    def update_api_key(self, api_key: str):
        self.api_key = api_key
        self._llm = None  # Force recreation with new api key 