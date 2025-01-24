from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class IntegrationConfig:
    """Immutable configuration container for integration instances."""
    name: str
    category: str
    attributes: Dict[str, Any]
