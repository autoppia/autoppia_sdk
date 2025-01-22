from autoppia_sdk.src.integrations.models import IntegrationConfig
from autoppia_sdk.src.integrations.implementations.email.smtp_integration import SMPTEmailIntegration
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.integrations.implementations.base import Integration


class IntegrationConfigAdapter():
    def from_autoppia_backend(worker_config_dto):
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
    def __init__(self):
        self.integration_mapping = {
            "email": {
                "Smtp": SMPTEmailIntegration
            }
        }

    def from_autoppia_backend(self, worker_config_dto):
        integrations = {}
        for integration in worker_config_dto.user_integration:
            # Initialize category dict if not exists
            category = integration.integration_obj.category
            if category not in integrations:
                integrations[category] = {}
            
            print(integration)

            integration_config = IntegrationConfigAdapter.from_autoppia_backend(integration)
            integration_class = self.integration_mapping[integration_config.category][integration_config.name]
            integration_instance = integration_class(integration_config)
            integrations[category][integration_config.name] = integration_instance

        return integrations
