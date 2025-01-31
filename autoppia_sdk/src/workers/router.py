import requests
from autoppia_sdk.src.workers.adapter import AIWorkerConfigAdapter

class WorkerRouter():
    @classmethod
    def from_id(cls, worker_id: str):
        """Fetches worker configuration using the adapter"""
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
        self.ip = ip
        self.port = port
    
    def call(self, message: str):
        """Makes a POST request to the worker endpoint with the message"""
        try:
            url = f"http://{self.ip}:{self.port}/process"
            response = requests.post(url, json={"message": message})
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.json()["result"]
        except Exception as e:
            raise Exception(f"Failed to call worker: {str(e)}")
        
    