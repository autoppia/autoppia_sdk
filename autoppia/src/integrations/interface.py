from abc import ABC


class IntegrationInterface(ABC):
    """Base class for all integrations that can be used by agents.
    
    This abstract base class serves as an interface that all integration implementations
    must inherit from. Integrations provide ways for agents to interact with external
    services, APIs, or systems.

    Examples:
        To create a new integration:

        ```python
        class MyIntegration(IntegrationInterface):
            def __init__(self):
                # Initialize integration-specific configuration
                pass
        ```
    """
    pass
