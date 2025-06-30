from autoppia.src.integrations.interface import IntegrationInterface


class Integration(IntegrationInterface):
    """Base Integration class that implements the IntegrationInterface.
    
    This class serves as a base implementation for all integration types in the Autoppia SDK.
    It inherits from IntegrationInterface and can be extended by specific integration
    implementations to provide custom functionality.

    Example:
        class CustomIntegration(Integration):
            def __init__(self):
                super().__init__()
                # Custom initialization code
    """
    pass
