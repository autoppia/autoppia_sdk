import requests

class WorkerRouter():
    @classmethod
    def from_id(cls, worker_id: int):
        """Fetches worker IP and port from the info endpoint"""
        try:
            response = requests.get("http://3.251.99.81/info")
            data = response.json()
            ip = data.get("ip")
            port = data.get("port")
            
            if not ip or not port:
                raise ValueError("Invalid response: missing ip or port")
                
            return cls(ip, port)
        except Exception as e:
            raise Exception(f"Failed to fetch worker info: {str(e)}")
    
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
    
    def call(self, message: str):
        """Makes a POST request to the worker endpoint with the message"""
        try:
            url = f"http://{self.ip}:{self.port}"
            response = requests.post(url, json={"message": message})
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.json()["result"]
        except Exception as e:
            raise Exception(f"Failed to call worker: {str(e)}")
        
    