"""
Multi-LLM Worker Example

This example demonstrates how to create an AI worker that can use multiple
LLM providers including OpenAI, Anthropic, Google Gemini, Cohere, HuggingFace,
Ollama, and local models.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from autoppia.src.workers.interface import AIWorker, WorkerConfig
from autoppia.src.llms import (
    LLMRegistry, 
    OpenAIService, 
    AnthropicService,
    GoogleGeminiService,
    CohereService,
    HuggingFaceService,
    OllamaService,
    LocalLLMService
)
from autoppia.src.exceptions import WorkerStartupError, WorkerExecutionError

logger = logging.getLogger(__name__)


class MultiLLMWorker(AIWorker):
    """
    A multi-LLM worker that can switch between different language model providers.
    
    This worker demonstrates how to:
    1. Configure multiple LLM services
    2. Switch between different providers
    3. Handle provider-specific configurations
    4. Fallback to alternative providers if one fails
    """
    
    def __init__(self, config: WorkerConfig):
        """Initialize the multi-LLM worker with configuration."""
        self.config = config
        self.current_provider = None
        self.llm_services = {}
        self.is_running = False
        
        logger.info(f"Initialized MultiLLMWorker: {config.name}")
    
    def start(self) -> None:
        """Start the worker and initialize all LLM services."""
        try:
            logger.info(f"Starting MultiLLMWorker: {self.config.name}")
            
            # Initialize all configured LLM services
            if self.config.llms:
                for provider_name, service in self.config.llms.items():
                    self.llm_services[provider_name] = service
                    logger.info(f"Initialized LLM service: {provider_name}")
                
                # Set default provider (first one)
                self.current_provider = list(self.config.llms.keys())[0]
                logger.info(f"Default LLM provider set to: {self.current_provider}")
            
            # Initialize integrations if configured
            if self.config.integrations:
                logger.info(f"Initialized {len(self.config.integrations)} integrations")
            
            self.is_running = True
            logger.info(f"MultiLLMWorker {self.config.name} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MultiLLMWorker {self.config.name}: {e}")
            raise WorkerStartupError(f"Worker startup failed: {e}")
    
    def stop(self) -> None:
        """Stop the worker and clean up resources."""
        try:
            logger.info(f"Stopping MultiLLMWorker: {self.config.name}")
            
            # Clean up any resources
            self.llm_services = {}
            self.current_provider = None
            self.is_running = False
            
            logger.info(f"MultiLLMWorker {self.config.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping MultiLLMWorker {self.config.name}: {e}")
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different LLM provider.
        
        Args:
            provider_name: Name of the provider to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if provider_name in self.llm_services:
            self.current_provider = provider_name
            logger.info(f"Switched to LLM provider: {provider_name}")
            return True
        else:
            logger.warning(f"Provider {provider_name} not available")
            return False
    
    def get_available_providers(self) -> list:
        """Get list of available LLM providers."""
        return list(self.llm_services.keys())
    
    def call(self, message: str) -> str:
        """Process a message using the current LLM provider."""
        if not self.is_running:
            raise WorkerExecutionError("Worker is not running")
        
        if not self.llm_services:
            return "No LLM services configured"
        
        try:
            logger.info(f"Processing message with provider {self.current_provider}: {message[:100]}...")
            
            # Use system prompt if configured
            system_prompt = self.config.system_prompt or "You are a helpful AI assistant."
            
            # Get current LLM service
            current_service = self.llm_services[self.current_provider]
            llm = current_service.get_llm()
            
            # Create a prompt with system message and user input
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            # Generate response using current LLM
            response = llm.predict(full_prompt)
            logger.info(f"Generated response using {self.current_provider}: {response[:100]}...")
            
            return response
                
        except Exception as e:
            logger.error(f"Error processing message with {self.current_provider}: {e}")
            
            # Try to fallback to another provider
            fallback_provider = self._get_fallback_provider()
            if fallback_provider:
                logger.info(f"Falling back to provider: {fallback_provider}")
                self.current_provider = fallback_provider
                return self.call(message)  # Recursive call with new provider
            else:
                raise WorkerExecutionError(f"All LLM providers failed: {e}")
    
    def _get_fallback_provider(self) -> Optional[str]:
        """Get a fallback provider if current one fails."""
        available_providers = list(self.llm_services.keys())
        if len(available_providers) > 1:
            # Return first provider that's not the current one
            for provider in available_providers:
                if provider != self.current_provider:
                    return provider
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the worker."""
        return {
            "name": self.config.name,
            "is_running": self.is_running,
            "current_provider": self.current_provider,
            "available_providers": self.get_available_providers(),
            "integrations_count": len(self.config.integrations),
            "system_prompt": self.config.system_prompt is not None
        }


async def main():
    """Example usage of the MultiLLMWorker with multiple providers."""
    
    # Create worker configuration with multiple LLM services
    config = WorkerConfig(
        name="multi-llm-worker",
        system_prompt="You are a helpful AI assistant that provides clear and concise answers.",
        llms={
            "openai": OpenAIService(
                api_key="your-openai-api-key",
                model="gpt-4o"
            ),
            "gemini": GoogleGeminiService(
                api_key="your-google-api-key",
                model="gemini-pro"
            ),
            "anthropic": AnthropicService(
                api_key="your-anthropic-api-key",
                model="claude-3-opus-20240229"
            ),
            "cohere": CohereService(
                api_key="your-cohere-api-key",
                model="command"
            ),
            "huggingface": HuggingFaceService(
                api_key="your-huggingface-api-key",
                model="meta-llama/Llama-2-7b-chat-hf"
            ),
            "ollama": OllamaService(
                model="llama2",
                base_url="http://localhost:11434"
            )
        }
    )
    
    # Create and start worker
    worker = MultiLLMWorker(config)
    
    try:
        worker.start()
        
        # Show available providers
        providers = worker.get_available_providers()
        print(f"Available LLM providers: {providers}")
        
        # Test with different providers
        test_message = "What is the capital of France?"
        
        # Test with current provider
        print(f"\nTesting with provider: {worker.current_provider}")
        response = worker.call(test_message)
        print(f"Question: {test_message}")
        print(f"Response: {response}")
        
        # Switch to a different provider
        if "gemini" in providers:
            worker.switch_provider("gemini")
            print(f"\nSwitched to provider: {worker.current_provider}")
            response = worker.call(test_message)
            print(f"Response: {response}")
        
        # Get worker status
        status = worker.get_status()
        print(f"\nWorker Status: {status}")
        
    finally:
        worker.stop()


def create_local_model_example():
    """Example of using local models."""
    
    # Example with local Llama model
    local_config = WorkerConfig(
        name="local-llm-worker",
        system_prompt="You are a helpful AI assistant.",
        llms={
            "local-llama": LocalLLMService(
                model_path="/path/to/llama-2-7b.gguf",
                model_type="llama"
            ),
            "local-gpt4all": LocalLLMService(
                model_path="/path/to/gpt4all-model.bin",
                model_type="gpt4all"
            )
        }
    )
    
    print("Local model configuration created:")
    print(f"Config: {local_config.name}")
    print(f"LLM services: {list(local_config.llms.keys())}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    
    # Show local model example
    create_local_model_example()
