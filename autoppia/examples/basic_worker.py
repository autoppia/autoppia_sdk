"""
Basic Worker Example

This example demonstrates how to create a simple AI worker using the Autoppia SDK.
The worker can process text messages and respond using configured LLM services.
"""

import asyncio
import logging
from typing import Dict, Any
from autoppia.src.workers.interface import AIWorker, WorkerConfig
from autoppia.src.llms import LLMRegistry, OpenAIService
from autoppia.src.exceptions import WorkerStartupError, WorkerExecutionError

logger = logging.getLogger(__name__)


class BasicWorker(AIWorker):
    """
    A basic AI worker that can process text messages and respond using LLM services.
    
    This worker demonstrates the basic pattern for implementing AI workers:
    1. Initialize with configuration
    2. Start up required services
    3. Process incoming messages
    4. Clean up resources on shutdown
    """
    
    def __init__(self, config: WorkerConfig):
        """Initialize the basic worker with configuration."""
        self.config = config
        self.llm_service = None
        self.is_running = False
        
        logger.info(f"Initialized BasicWorker: {config.name}")
    
    def start(self) -> None:
        """Start the worker and initialize required services."""
        try:
            logger.info(f"Starting BasicWorker: {self.config.name}")
            
            # Initialize LLM service if configured
            if self.config.llms:
                provider_name = list(self.config.llms.keys())[0]
                self.llm_service = self.config.llms[provider_name]
                logger.info(f"Initialized LLM service: {provider_name}")
            
            # Initialize integrations if configured
            if self.config.integrations:
                logger.info(f"Initialized {len(self.config.integrations)} integrations")
            
            self.is_running = True
            logger.info(f"BasicWorker {self.config.name} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start BasicWorker {self.config.name}: {e}")
            raise WorkerStartupError(f"Worker startup failed: {e}")
    
    def stop(self) -> None:
        """Stop the worker and clean up resources."""
        try:
            logger.info(f"Stopping BasicWorker: {self.config.name}")
            
            # Clean up any resources
            self.llm_service = None
            self.is_running = False
            
            logger.info(f"BasicWorker {self.config.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping BasicWorker {self.config.name}: {e}")
    
    def call(self, message: str) -> str:
        """Process a message and return a response."""
        if not self.is_running:
            raise WorkerExecutionError("Worker is not running")
        
        try:
            logger.info(f"Processing message: {message[:100]}...")
            
            # Use system prompt if configured
            system_prompt = self.config.system_prompt or "You are a helpful AI assistant."
            
            # If we have an LLM service, use it to generate response
            if self.llm_service:
                llm = self.llm_service.get_llm()
                
                # Create a prompt with system message and user input
                full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
                
                # Generate response using LLM
                response = llm.predict(full_prompt)
                logger.info(f"Generated response using LLM: {response[:100]}...")
                
                return response
            
            else:
                # Fallback response if no LLM service
                return f"Hello! I'm {self.config.name}. I received your message: '{message}'. However, I don't have an LLM service configured to process it."
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise WorkerExecutionError(f"Message processing failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the worker."""
        return {
            "name": self.config.name,
            "is_running": self.is_running,
            "has_llm": self.llm_service is not None,
            "integrations_count": len(self.config.integrations),
            "system_prompt": self.config.system_prompt is not None
        }


async def main():
    """Example usage of the BasicWorker."""
    
    # Create worker configuration
    config = WorkerConfig(
        name="example-worker",
        system_prompt="You are a helpful AI assistant that provides clear and concise answers.",
        llms={
            "openai": OpenAIService(
                api_key="your-openai-api-key",
                model="gpt-4o"
            )
        }
    )
    
    # Create and start worker
    worker = BasicWorker(config)
    
    try:
        worker.start()
        
        # Test the worker
        test_message = "What is the capital of France?"
        response = worker.call(test_message)
        print(f"Question: {test_message}")
        print(f"Response: {response}")
        
        # Get worker status
        status = worker.get_status()
        print(f"Worker Status: {status}")
        
    finally:
        worker.stop()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
