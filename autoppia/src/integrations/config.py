from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class IntegrationConfig:
    """Immutable configuration container for integration instances.
    
    This class provides a standardized way to store and access configuration
    settings for different types of integrations. The frozen=True decorator
    ensures that the configuration remains immutable after instantiation.

    Attributes:
        name (str): The unique identifier or name of the integration.
        category (str): The category or type of integration (e.g., 'database',
            'messaging', 'storage', etc.).
        attributes (Dict[str, Any]): A dictionary containing configuration
            parameters specific to the integration. Keys are parameter names
            and values can be of any type.

    Example:
        >>> config = IntegrationConfig(
        ...     name="mysql_prod",
        ...     category="database",
        ...     attributes={
        ...         "host": "localhost",
        ...         "port": 3306,
        ...         "username": "user"
        ...     }
        ... )
    """
    name: str
    category: str
    attributes: Dict[str, Any]
