import requests
from autoppia_sdk.src.workers.adapter import AIWorkerConfigAdapter

class WorkerRouter():
    """A router class for handling communication with AI workers.

    This class manages the routing and communication with AI worker instances,
    handling configuration retrieval and message processing.
    """

    @classmethod
    def from_id(cls, worker_id: str):
        """Creates a WorkerRouter instance from a worker ID.

        Args:
            worker_id (str): The unique identifier of the worker.

        Returns:
            WorkerRouter: A new instance configured with the worker's IP and port.

        Raises:
            ValueError: If the configuration is missing IP or port.
            Exception: If worker configuration fetch fails.
        """
        try:
            # Initialize adapter with worker_id
            adapter = AIWorkerConfigAdapter(worker_id)
            
            # Get worker configuration
            worker_config = adapter.from_autoppia_user_backend()
            
            if not worker_config.ip or not worker_config.port:
                raise ValueError("Invalid configuration: missing ip or port")
                
            return cls(worker_config.ip, worker_config.port)
        except Exception as e:
            raise Exception(f"Failed to fetch worker config: {str(e)}")
    
    def __init__(self, ip: str, port: int):
        """Initializes a WorkerRouter instance.

        Args:
            ip (str): The IP address of the worker.
            port (int): The port number the worker is listening on.
        """
        self.ip = ip
        self.port = port
    
    def call(self, message: str):
        """Sends a message to the worker for processing.

        Makes a POST request to the worker's endpoint with the provided message
        and returns the processed result.

        Args:
            message (str): The message to be processed by the worker.

        Returns:
            Any: The processed result from the worker.

        Raises:
            Exception: If the worker call fails or returns an error status.
        """
        try:
            url = f"http://{self.ip}:{self.port}/process"
            response = requests.post(url, json={"message": message})
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.json()["result"]
        except Exception as e:
            raise Exception(f"Failed to call worker: {str(e)}")
        
    