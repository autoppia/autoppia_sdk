"""
LLM Service Providers for Autoppia SDK

This module provides implementations for various language model providers
including OpenAI, Anthropic, Google Gemini, Cohere, and HuggingFace.
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere
from langchain_huggingface import HuggingFaceEndpoint
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


class GoogleGeminiService(LLMServiceInterface):
    """Google Gemini language model service implementation.
    
    This class provides an interface to Google's Gemini models through the LangChain
    integration. It handles model initialization, API key management, and model updates.
    
    Attributes:
        api_key (str): Google AI API key for authentication
        model (str): Name of the Gemini model to use (default: "gemini-pro")
        _llm (BaseLanguageModel): Cached LangChain ChatGoogleGenerativeAI instance
    """

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        """Initialize the Google Gemini service.
        
        Args:
            api_key (str): Google AI API key for authentication
            model (str, optional): Name of the Gemini model. Defaults to "gemini-pro"
        """
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain ChatGoogleGenerativeAI instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain ChatGoogleGenerativeAI instance
        """
        if not self._llm:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                convert_system_message_to_human=True
            )
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
            api_key (str): New API keyemis to use
        """
        self.api_key = api_key
        self._llm = None


class CohereService(LLMServiceInterface):
    """Cohere language model service implementation.
    
    This class provides an interface to Cohere's language models through the LangChain
    integration. It handles model initialization, API key management, and model updates.
    
    Attributes:
        api_key (str): Cohere API key for authentication
        model (str): Name of the Cohere model to use (default: "command")
        _llm (BaseLanguageModel): Cached LangChain ChatCohere instance
    """

    def __init__(self, api_key: str, model: str = "command"):
        """Initialize the Cohere service.
        
        Args:
            api_key (str): Cohere API key for authentication
            model (str, optional): Name of the Cohere model. Defaults to "command"
        """
        self.api_key = api_key
        self.model = model
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain ChatCohere instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain ChatCohere instance
        """
        if not self._llm:
            self._llm = ChatCohere(
                model=self.model,
                cohere_api_key=self.api_key
            )
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


class HuggingFaceService(LLMServiceInterface):
    """HuggingFace language model service implementation.
    
    This class provides an interface to HuggingFace's language models through the LangChain
    integration. It handles model initialization, API key management, and model updates.
    
    Attributes:
        api_key (str): HuggingFace API key for authentication
        model (str): Name of the HuggingFace model to use
        endpoint_url (str): HuggingFace endpoint URL
        _llm (BaseLanguageModel): Cached LangChain HuggingFaceEndpoint instance
    """

    def __init__(self, api_key: str, model: str, endpoint_url: str = None):
        """Initialize the HuggingFace service.
        
        Args:
            api_key (str): HuggingFace API key for authentication
            model (str): Name of the HuggingFace model to use
            endpoint_url (str, optional): Custom endpoint URL. Defaults to None.
        """
        self.api_key = api_key
        self.model = model
        self.endpoint_url = endpoint_url
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain HuggingFaceEndpoint instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain HuggingFaceEndpoint instance
        """
        if not self._llm:
            kwargs = {
                "huggingfacehub_api_token": self.api_key,
                "task": "text-generation"
            }
            
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            
            self._llm = HuggingFaceEndpoint(**kwargs)
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


class OllamaService(LLMServiceInterface):
    """Ollama local language model service implementation.
    
    This class provides an interface to Ollama's local language models through the LangChain
    integration. It handles model initialization and model updates.
    
    Attributes:
        model (str): Name of the Ollama model to use (default: "llama2")
        base_url (str): Ollama base URL (default: "http://localhost:11434")
        _llm (BaseLanguageModel): Cached LangChain Ollama instance
    """

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        """Initialize the Ollama service.
        
        Args:
            model (str, optional): Name of the Ollama model. Defaults to "llama2"
            base_url (str, optional): Ollama base URL. Defaults to "http://localhost:11434"
        """
        self.model = model
        self.base_url = base_url
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain Ollama instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain Ollama instance
        """
        if not self._llm:
            try:
                from langchain_community.llms import Ollama
                self._llm = Ollama(
                    model=self.model,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError("langchain-community is required for Ollama support")
        return self._llm

    def update_model(self, model_name: str) -> None:
        """Update the model name and reset the LLM instance.
        
        Args:
            model_name (str): New model name to use
        """
        self.model = model_name
        self._llm = None

    def update_api_key(self, api_key: str) -> None:
        """Update the API key (not applicable for Ollama).
        
        Args:
            api_key (str): API key (ignored for Ollama)
        """
        # Ollama doesn't use API keys
        pass


class LocalLLMService(LLMServiceInterface):
    """Local language model service implementation.
    
    This class provides an interface to local language models through the LangChain
    integration. It handles model initialization and model updates.
    
    Attributes:
        model_path (str): Path to the local model
        model_type (str): Type of local model (e.g., "llama", "gpt4all")
        _llm (BaseLanguageModel): Cached LangChain local model instance
    """

    def __init__(self, model_path: str, model_type: str = "llama"):
        """Initialize the local LLM service.
        
        Args:
            model_path (str): Path to the local model
            model_type (str, optional): Type of local model. Defaults to "llama"
        """
        self.model_path = model_path
        self.model_type = model_type
        self._llm = None

    def get_llm(self) -> BaseLanguageModel:
        """Get or create the LangChain local model instance.
        
        Returns:
            BaseLanguageModel: Configured LangChain local model instance
        """
        if not self._llm:
            try:
                if self.model_type.lower() == "llama":
                    from langchain_community.llms import LlamaCpp
                    self._llm = LlamaCpp(
                        model_path=self.model_path,
                        n_ctx=2048,
                        n_threads=4
                    )
                elif self.model_type.lower() == "gpt4all":
                    from langchain_community.llms import GPT4All
                    self._llm = GPT4All(
                        model=self.model_path,
                        n_threads=4
                    )
                else:
                    raise ValueError(f"Unsupported local model type: {self.model_type}")
            except ImportError:
                raise ImportError("langchain-community is required for local model support")
        return self._llm

    def update_model(self, model_name: str) -> None:
        """Update the model path and reset the LLM instance.
        
        Args:
            model_name (str): New model path to use
        """
        self.model_path = model_name
        self._llm = None

    def update_api_key(self, api_key: str) -> None:
        """Update the API key (not applicable for local models).
        
        Args:
            api_key (str): API key (ignored for local models)
        """
        # Local models don't use API keys
        pass 