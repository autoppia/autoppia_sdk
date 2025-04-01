import json
import logging
import requests
import time
from typing import Dict, Optional, Any, Callable
from autoppia_sdk.src.workers.router import WorkerRouter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AppRouter")

class AppRouter(WorkerRouter):
    """A router class for handling communication with AI applications via Socket.IO.

    This class extends the WorkerRouter to provide additional functionality for
    routing messages to specific workers within an application and handling
    application-specific operations.
    """

    @classmethod
    def from_id(cls, app_id: int):
        """Fetches app IP and port from the info endpoint"""
        try:
            payload = {
                "SECRET": "ekwklrklkfewf3232nm",
                "id": app_id,
                "type": "app"  # Specify that we're looking for an app, not a worker
            }
            logger.info(f"Fetching app info for app_id: {app_id}")
            response = requests.get("http://3.251.99.81/info", json=payload)
            data = response.json()
            logger.info(f"Received app info: {data}")
            ip = data.get("ip")
            port = data.get("port")
            
            if not ip or not port:
                logger.error(f"Invalid response: missing ip or port. Response: {data}")
                raise ValueError("Invalid response: missing ip or port")
                
            return cls(ip, port)
        except Exception as e:
            logger.error(f"Failed to fetch app info: {str(e)}")
            raise Exception(f"Failed to fetch app info: {str(e)}")
    
    def __init__(self, ip: str, port: int):
        """Initializes an AppRouter instance.

        Args:
            ip (str): The IP address of the app.
            port (int): The port number the app is listening on.
        """
        super().__init__(ip, port)
        logger.info(f"Initialized AppRouter with SocketIO URL: {self.socketio_url}")
    
    def call_worker(self, message: str, worker_name: str, stream_callback=None, keep_alive=False):
        """Sends a message to a specific worker within the app for processing.
        
        Args:
            message (str): The message to send to the worker
            worker_name (str): The name of the worker to route the message to
            stream_callback (callable, optional): Callback function to handle streaming responses
            keep_alive (bool, optional): If True, the connection will be kept alive indefinitely
        
        Returns:
            The final result from the worker
        """
        # Wrap the message with worker routing information
        routed_message = {
            "message": message,
            "worker": worker_name
        }
        
        # Use the parent class's call method with the routed message
        return super().call(json.dumps(routed_message), stream_callback, keep_alive)
    
    def get_app_info(self, stream_callback=None):
        """Retrieves information about the app.
        
        Args:
            stream_callback (callable, optional): Callback function to handle streaming responses
        
        Returns:
            Dictionary containing app information
        """
        info_request = {
            "action": "get_app_info"
        }
        
        return super().call(json.dumps(info_request), stream_callback)
    
    def get_ui_config(self, stream_callback=None):
        """Retrieves the UI configuration for the app.
        
        Args:
            stream_callback (callable, optional): Callback function to handle streaming responses
        
        Returns:
            Dictionary containing UI configuration
        """
        ui_request = {
            "action": "get_ui_config"
        }
        
        return super().call(json.dumps(ui_request), stream_callback)
    
    def get_available_workers(self, stream_callback=None):
        """Retrieves a list of available workers in the app.
        
        Args:
            stream_callback (callable, optional): Callback function to handle streaming responses
        
        Returns:
            Dictionary containing worker information
        """
        workers_request = {
            "action": "get_workers"
        }
        
        return super().call(json.dumps(workers_request), stream_callback)
