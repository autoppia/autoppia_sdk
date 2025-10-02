from abc import ABC, abstractmethod
from autoppia.src.integrations.interface import IntegrationInterface
from autoppia.src.llms.interface import LLMServiceInterface
from autoppia.src.vectorstores.interface import VectorStoreInterface
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class WorkerConfig:
    """Configuration container for worker instances.
    
    Attributes:
        name: Unique identifier for the worker configuration
        system_prompt: Base prompt template for the worker
        ip: IP address of the worker
        port: Port number of the worker
        integrations: Dictionary of integration clients keyed by provider
        llms: Dictionary of LLM services keyed by provider
        vectorstore: Dictionary of vector stores keyed by provider
        extra_arguments: Additional provider-specific configuration parameters

    """
    
    name: str
    llm: LLMServiceInterface
    vectorstore: VectorStoreInterface
    system_prompt: Optional[str] = None
    mcp: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    integrations: Dict[str, IntegrationInterface] = field(default_factory=dict)
    extra_arguments: Dict[str, Any] = field(default_factory=dict)
    template_id: str


class AIWorker(ABC):
    """Base interface that all marketplace agents must implement.
    
    This abstract class defines the core interface that all AI workers/agents
    must implement to be compatible with the Autoppia SDK. It provides the basic
    lifecycle and interaction methods required for agent operation.
    """

    @abstractmethod
    def start(self) -> None:
        """Initialize the agent and any required resources.
        
        This method should handle any necessary setup steps such as:
        - Loading models or configurations
        - Establishing connections to services
        - Initializing internal state
        - Allocating resources
        
        Should be called before any calls to the agent are made.
        """

    @abstractmethod
    def stop(self) -> None:
        """Cleanup and release any resources.
        
        This method should handle proper cleanup including:
        - Closing connections
        - Releasing memory/compute resources
        - Saving any persistent state
        - General cleanup tasks
        
        Should be called when the agent is no longer needed.
        """

    @abstractmethod
    def call(self, message: str) -> str:
        """Process a message and return a response.
        
        Args:
            message: The input message/query to be processed by the agent
            
        Returns:
            str: The agent's response to the input message
            
        This is the main interaction method where the agent processes
        input and generates appropriate responses based on its configuration
        and capabilities.
        """
