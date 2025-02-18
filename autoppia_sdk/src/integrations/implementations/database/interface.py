from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class DatabaseIntegration(ABC):
    @abstractmethod
    def execute_sql(
        self,
        sql: str,
    ):
        
        pass
