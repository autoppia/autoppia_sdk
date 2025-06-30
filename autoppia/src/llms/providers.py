from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema.language_model import BaseLanguageModel
from autoppia.src.llms.interface import LLMServiceInterface

class OpenAIService(LLMServiceInterface):
    """OpenAI language model service implementation.
    
    This class provides an interface to OpenAI's language models through the LangChain
    integration. It handles model initialization, API key management, and model updates.
    
    Attributes:
        api_key (str): OpenAI API key for authentication
        model (str): Name of the OpenAI model to use (default: "gpt-4o")
        _llm (BaseLanguageModel): Cached LangChain ChatOpenAI instance
    """

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """Initialize the OpenAI service.
        
        Args:
            api_key (str): OpenAI API key for authentication
            model (str, optional): Name of the OpenAI model. Defaults to "gpt-4o"
        """
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain ChatOpenAI instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain ChatOpenAI instance
        """
        if not self._llm:
            self._llm = ChatOpenAI(model=self.model, api_key=self.api_key)
        return self._llm

    def update_model(self, model_name: str) -> None:
        """Update the model name and reset the LLM instance.
        
        Args:
            model_name (str): New model name to use
        """
        self.model = model_name
        self._llm = None

    def update_api_key(self, api_key: str) -> None:
        """Update the API key and reset the LLM instance.
        
        Args:
            api_key (str): New API key to use
        """
        self.api_key = api_key
        self._llm = None

class AnthropicService(LLMServiceInterface):
    """Anthropic language model service implementation.
    
    This class provides an interface to Anthropic's language models through the LangChain
    integration. It handles model initialization, API key management, and model updates.
    
    Attributes:
        api_key (str): Anthropic API key for authentication
        model (str): Name of the Anthropic model to use (default: "claude-3-opus-20240229")
        _llm (BaseLanguageModel): Cached LangChain ChatAnthropic instance
    """

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """Initialize the Anthropic service.
        
        Args:
            api_key (str): Anthropic API key for authentication
            model (str, optional): Name of the Anthropic model. Defaults to "claude-3-opus-20240229"
        """
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain ChatAnthropic instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain ChatAnthropic instance
        """
        if not self._llm:
            self._llm = ChatAnthropic(model=self.model, anthropic_api_key=self.api_key)
        return self._llm

    def update_model(self, model_name: str) -> None:
        """Update the model name and reset the LLM instance.
        
        Args:
            model_name (str): New model name to use
        """
        self.model = model_name
        self._llm = None

    def update_api_key(self, api_key: str) -> None:
        """Update the API key and reset the LLM instance.
        
        Args:
            api_key (str): New API key to use
        """
        self.api_key = api_key
        self._llm = None 