from autoppia_sdk.src.integrations.config import IntegrationConfig
from autoppia_sdk.src.integrations.implementations.email.smtp_integration import SMPTEmailIntegration
from autoppia_sdk.src.integrations.implementations.database.postgres_integration import PostgresIntegration
from autoppia_sdk.src.integrations.implementations.api.api_integration import AutoppiaIntegration
from autoppia_sdk.src.integrations.implementations.software.web_search_integration import WebSearchIntegration
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.integrations.implementations.base import Integration


class IntegrationConfigAdapter():
    """
    Adapter class for converting backend integration configuration data to IntegrationConfig objects.
    """
    
    @staticmethod
    def from_autoppia_backend(worker_config_dto):
        """
        Converts backend worker configuration DTO to an IntegrationConfig object.

        Args:
            worker_config_dto: DTO containing integration configuration from the backend

        Returns:
            IntegrationConfig: Configuration object with integration name, category, and attributes
        """
        # Convert attributes list to dictionary
        attributes = {}
        for attr in worker_config_dto.user_integration_attributes:
            value = attr.value
            # If credential exists, use the credential value
            if attr.credential_obj:
                value = attr.credential_obj.credential
            attributes[attr.integration_attribute_obj.name] = value

        integration_config = IntegrationConfig(
            worker_config_dto.integration_obj.name,
            worker_config_dto.integration_obj.category,
            attributes
        )
        return integration_config

class IntegrationsAdapter():
    """
    Adapter class for managing and instantiating integration implementations based on backend configuration.
    """

    def __init__(self):
        """
        Initializes the adapter with a mapping of available integration implementations.
        The mapping follows the structure: {category: {name: implementation_class}}
        """
        self.integration_mapping = {
            "email": {
                "Smtp": SMPTEmailIntegration
            },
            "database": {
                "Postgres": PostgresIntegration
            },
            "api": {
                "Autoppia": AutoppiaIntegration
            },
            "software": {
                "Web Search": WebSearchIntegration
            }
        }

    def from_autoppia_backend(self, worker_config_dto):
        """
        Creates integration instances from backend worker configuration.

        Args:
            worker_config_dto: DTO containing integration configurations from the backend

        Returns:
            dict: Nested dictionary of instantiated integrations organized by category and name
                 Structure: {category: {name: integration_instance}}
        """
        integrations = {}
        for integration in worker_config_dto.user_integration:
            # Initialize category dict if not exists
            category = integration.integration_obj.category
            if category not in integrations:
                integrations[category] = {}

            integration_config = IntegrationConfigAdapter.from_autoppia_backend(integration)
            integration_class = self.integration_mapping[integration_config.category][integration_config.name]
            integration_instance = integration_class(integration_config)
            integrations[category][integration_config.name] = integration_instance

        return integrations
