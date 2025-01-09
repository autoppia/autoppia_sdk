import requests

class WorkersAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def call(self, message: str) -> dict:
        """Call the worker with a message"""
        response = requests.post(
            f"{self.base_url}/process",
            json={"message": message}
        )
        return response.json()