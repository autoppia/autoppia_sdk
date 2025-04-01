from typing import Dict, Optional, Any, Callable, List
import logging
import json
from autoppia_sdk.src.apps.base_app import BaseAIApp
from autoppia_sdk.src.apps.interface import AppConfig
from autoppia_sdk.src.workers.interface import AIWorker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ChatbotApp")


class ChatbotApp(BaseAIApp):
    """Example implementation of a chatbot application.
    
    This class demonstrates how to implement a chatbot application that uses
    multiple workers for different types of queries.
    
    Attributes:
        APP_TYPE: The type of app, used for registration with the AppFactory
        config: The configuration for the app
        workers: Dictionary of worker instances keyed by worker name
        conversation_history: Dictionary of conversation histories keyed by session ID
    """
    
    APP_TYPE = "chatbot"
    
    def __init__(self, config: AppConfig):
        """Initialize the ChatbotApp.
        
        Args:
            config: The configuration for the app
        """
        super().__init__(config)
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.worker_specialties: Dict[str, List[str]] = {}
    
    def start(self) -> None:
        """Initialize the app and any required resources."""
        super().start()
        
        # Initialize worker specialties from config
        if self.config.extra_arguments and "worker_specialties" in self.config.extra_arguments:
            self.worker_specialties = self.config.extra_arguments["worker_specialties"]
        else:
            # Default specialties based on worker names
            for worker_name in self.workers.keys():
                if "math" in worker_name.lower():
                    self.worker_specialties[worker_name] = ["math", "calculation", "number"]
                elif "code" in worker_name.lower():
                    self.worker_specialties[worker_name] = ["code", "programming", "developer"]
                elif "writing" in worker_name.lower():
                    self.worker_specialties[worker_name] = ["write", "essay", "content"]
                else:
                    self.worker_specialties[worker_name] = []
        
        logger.info(f"Initialized worker specialties: {self.worker_specialties}")
    
    def route_message(self, message: str, worker_name: Optional[str] = None, session_id: str = "default") -> str:
        """Route a message to a specific worker or determine the appropriate worker.
        
        This implementation uses a simple keyword-based routing strategy to determine
        which worker to route the message to based on the message content.
        
        Args:
            message: The input message to be processed
            worker_name: Optional name of the worker to route the message to
            session_id: Optional session ID for tracking conversation history
            
        Returns:
            str: The response from the worker
        """
        if not self._initialized:
            raise RuntimeError("App not initialized")
        
        if not self.workers:
            raise ValueError("No workers registered")
        
        # Initialize conversation history for this session if it doesn't exist
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add the user message to the conversation history
        self.conversation_history[session_id].append({
            "role": "user",
            "message": message
        })
        
        # If worker_name is provided, route to that worker
        if worker_name:
            if worker_name not in self.workers:
                raise ValueError(f"Worker {worker_name} not found")
            
            response = self.workers[worker_name].call(message)
            
            # Add the response to the conversation history
            self.conversation_history[session_id].append({
                "role": "assistant",
                "worker": worker_name,
                "message": response
            })
            
            return response
        
        # If no worker_name is provided, use a simple routing strategy
        # based on keywords in the message
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Calculate a score for each worker based on specialty keywords
        worker_scores = {name: 0 for name in self.workers.keys()}
        
        for worker_name, specialties in self.worker_specialties.items():
            for keyword in specialties:
                if keyword.lower() in message_lower:
                    worker_scores[worker_name] += 1
        
        # Get the worker with the highest score
        best_worker_name = max(worker_scores.items(), key=lambda x: x[1])[0]
        
        # If all scores are 0, use the first worker
        if worker_scores[best_worker_name] == 0:
            best_worker_name = next(iter(self.workers))
        
        logger.info(f"Routing message to worker: {best_worker_name}")
        
        # Call the selected worker
        response = self.workers[best_worker_name].call(message)
        
        # Add the response to the conversation history
        self.conversation_history[session_id].append({
            "role": "assistant",
            "worker": best_worker_name,
            "message": response
        })
        
        return response
    
    def call_stream(self, message: str, callback: Callable[[Any], None], worker_name: Optional[str] = None, session_id: str = "default") -> Optional[str]:
        """Process a message with streaming and return a final response.
        
        This implementation extends the parent class's implementation to include
        conversation history tracking.
        
        Args:
            message: The input message to be processed
            callback: Function to call with streaming chunks
            worker_name: Optional name of the worker to route the message to
            session_id: Optional session ID for tracking conversation history
            
        Returns:
            Optional[str]: The final response from the worker, if any
        """
        if not self._initialized:
            raise RuntimeError("App not initialized")
        
        if not self.workers:
            raise ValueError("No workers registered")
        
        # Initialize conversation history for this session if it doesn't exist
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add the user message to the conversation history
        self.conversation_history[session_id].append({
            "role": "user",
            "message": message
        })
        
        # Create a wrapper callback that adds the response to the conversation history
        final_response = []
        
        def history_callback(chunk):
            # Call the original callback
            callback(chunk)
            
            # Accumulate the response
            if isinstance(chunk, str):
                final_response.append(chunk)
            elif isinstance(chunk, dict) and "text" in chunk:
                final_response.append(chunk["text"])
        
        # If worker_name is provided, route to that worker
        if worker_name:
            if worker_name not in self.workers:
                raise ValueError(f"Worker {worker_name} not found")
            
            worker = self.workers[worker_name]
            
            # Check if the worker supports streaming
            if hasattr(worker, 'call_stream'):
                result = worker.call_stream(message, history_callback)
            else:
                # Fallback to non-streaming call
                result = worker.call(message)
                history_callback(result)
                result = None
            
            # Add the response to the conversation history
            self.conversation_history[session_id].append({
                "role": "assistant",
                "worker": worker_name,
                "message": "".join(final_response)
            })
            
            return result
        
        # If no worker_name is provided, use the routing strategy
        # from route_message to determine the appropriate worker
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Calculate a score for each worker based on specialty keywords
        worker_scores = {name: 0 for name in self.workers.keys()}
        
        for worker_name, specialties in self.worker_specialties.items():
            for keyword in specialties:
                if keyword.lower() in message_lower:
                    worker_scores[worker_name] += 1
        
        # Get the worker with the highest score
        best_worker_name = max(worker_scores.items(), key=lambda x: x[1])[0]
        
        # If all scores are 0, use the first worker
        if worker_scores[best_worker_name] == 0:
            best_worker_name = next(iter(self.workers))
        
        logger.info(f"Routing message to worker: {best_worker_name}")
        
        # Call the selected worker
        worker = self.workers[best_worker_name]
        
        # Check if the worker supports streaming
        if hasattr(worker, 'call_stream'):
            result = worker.call_stream(message, history_callback)
        else:
            # Fallback to non-streaming call
            result = worker.call(message)
            history_callback(result)
            result = None
        
        # Add the response to the conversation history
        self.conversation_history[session_id].append({
            "role": "assistant",
            "worker": best_worker_name,
            "message": "".join(final_response)
        })
        
        return result
    
    def get_conversation_history(self, session_id: str = "default") -> List[Dict[str, Any]]:
        """Retrieve the conversation history for a session.
        
        Args:
            session_id: The session ID to retrieve history for
            
        Returns:
            List[Dict[str, Any]]: The conversation history
        """
        return self.conversation_history.get(session_id, [])
    
    def clear_conversation_history(self, session_id: str = "default") -> None:
        """Clear the conversation history for a session.
        
        Args:
            session_id: The session ID to clear history for
        """
        if session_id in self.conversation_history:
            self.conversation_history[session_id] = []
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Retrieve the UI configuration for the application.
        
        Returns:
            Dict[str, Any]: The UI configuration
        """
        # Start with the base UI configuration
        ui_config = super().get_ui_config()
        
        # Add chatbot-specific UI configuration
        chatbot_ui = {
            "display_worker_name": True,
            "allow_worker_selection": True,
            "show_conversation_history": True,
            "theme": {
                "primary_color": "#007bff",
                "secondary_color": "#6c757d",
                "background_color": "#f8f9fa",
                "text_color": "#212529"
            }
        }
        
        # Merge with any existing UI configuration
        ui_config.update(chatbot_ui)
        
        return ui_config
    
    def get_app_info(self) -> Dict[str, Any]:
        """Retrieve information about the application.
        
        Returns:
            Dict[str, Any]: Information about the application
        """
        # Start with the base app info
        app_info = super().get_app_info()
        
        # Add chatbot-specific app info
        chatbot_info = {
            "app_type": "chatbot",
            "capabilities": ["conversation", "multi-worker", "specialty-routing"],
            "worker_specialties": self.worker_specialties
        }
        
        # Merge with any existing app info
        app_info.update(chatbot_info)
        
        return app_info
