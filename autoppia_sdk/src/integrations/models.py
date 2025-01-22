from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class IntegrationConfig:
    name: str
    category: str
    attributes: Dict[str, Any]
