from abc import ABC, abstractmethod
from typing import Any, Dict


class Integration(ABC):
    """Base class for all integrations that can be used by agents"""

    @abstractmethod
    def configure(self, user_config: Dict[str, Any]) -> None:
        """Configure the integration with user-specific settings"""

