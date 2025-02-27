import requests
from autoppia_sdk.src.workers.adapter import AIWorkerConfigAdapter

class WorkerRouter():
    """A router class for handling communication with AI workers.

    This class manages the routing and communication with AI worker instances,
    handling configuration retrieval and message processing.
    """

    @classmethod
    def from_id(cls, worker_id: int):
        """Fetches worker IP and port from the info endpoint"""
        try:
            payload = {
                "SECRET": "ekwklrklkfewf3232nm",
                "id": worker_id
            }
            response = requests.get("http://3.251.99.81/info", json=payload)
            data = response.json()
            ip = data.get("ip")
            port = data.get("port")
            
            if not ip or not port:
                raise ValueError("Invalid response: missing ip or port")
                
            return cls(ip, port)
        except Exception as e:
            raise Exception(f"Failed to fetch worker info: {str(e)}")
    
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
            url = f"http://{self.ip}:{self.port}/call"
            response = requests.post(url, json={"message": message})
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.json()["result"]
        except Exception as e:
            raise Exception(f"Failed to call worker: {str(e)}")
        
    