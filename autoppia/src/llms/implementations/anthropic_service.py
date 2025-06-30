from langchain_anthropic import ChatAnthropic
from autoppia.src.llms.interface import LLMServiceInterface

class AnthropicService(LLMServiceInterface):
    """Service class for interacting with Anthropic's language models.

    This class provides an interface to Anthropic's AI models (like Claude) through
    the LangChain integration. It implements the LLMServiceInterface.

    Attributes:
        api_key (str): The Anthropic API key for authentication.
        model (str): The name of the Anthropic model to use.
        _llm: Internal reference to the LangChain ChatAnthropic instance.
    """

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """Initialize the Anthropic service.

        Args:
            api_key (str): The Anthropic API key for authentication.
            model (str, optional): The model name to use. Defaults to "claude-3-opus-20240229".
        """
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self):
        """Get or create the LangChain ChatAnthropic instance.

        Returns:
            ChatAnthropic: A configured instance of the ChatAnthropic class.
        """
        if not self._llm:
            self._llm = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model=self.model,
                max_tokens=4096  # Optional: configure max output tokens
            )
        return self._llm

    def update_model(self, model_name: str):
        """Update the model name and reset the LLM instance.

        Args:
            model_name (str): The new model name to use.
        """
        self.model = model_name
        self._llm = None  # Force recreation with new model

    def update_api_key(self, api_key: str):
        """Update the API key and reset the LLM instance.

        Args:
            api_key (str): The new Anthropic API key.
        """
        self.api_key = api_key
        self._llm = None  # Force recreation with new api key 