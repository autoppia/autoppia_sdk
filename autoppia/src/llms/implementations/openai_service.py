from langchain_openai import ChatOpenAI
from autoppia.src.llms.interface import LLMServiceInterface

class OpenAIService(LLMServiceInterface):
    """OpenAI language model service implementation.
    
    This class provides an interface to OpenAI's language models through the LangChain
    integration. It handles model initialization, API key management, and model updates.
    
    Attributes:
        api_key (str): OpenAI API key for authentication
        model (str): Name of the OpenAI model to use (default: "gpt-4o")
        _llm (ChatOpenAI): Cached LangChain ChatOpenAI instance
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

    def get_llm(self):
        """Get or create the LangChain ChatOpenAI instance.
        
        Returns:
            ChatOpenAI: Configured LangChain ChatOpenAI instance
        """
        if not self._llm:
            self._llm = ChatOpenAI(
                openai_api_key=self.api_key,
                model=self.model
            )
        return self._llm

    def update_model(self, model_name: str):
        """Update the model name and reset the LLM instance.
        
        Args:
            model_name (str): New model name to use
        """
        self.model = model_name
        self._llm = None  # Force recreation with new model

    def update_api_key(self, api_key: str):
        """Update the API key and reset the LLM instance.
        
        Args:
            api_key (str): New API key to use
        """
        self.api_key = api_key
        self._llm = None  # Force recreation with new api key 