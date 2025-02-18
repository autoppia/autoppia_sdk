from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class SoftwareIntegration(ABC):
    

    @abstractmethod
    def call_endpoint(
        self,
        query: str,
        num_results: int = 5
    ):
       
        pass
