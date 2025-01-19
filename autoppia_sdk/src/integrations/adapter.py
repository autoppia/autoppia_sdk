from typing import Dict, Any
from dataclasses import dataclass
from autoppia_sdk.src.integrations.implementations.email.smtp_integration import (
    SMPTEmailIntegration)
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.integrations.implementations.base import Integration


@dataclass
class IntegrationConfig:
    name: str
    category: str
    attributes: Dict[str, Any]


class IntegrationConfigAdapter():
    def from_autoppia_backend(worker_config_dto):
        integration_config = IntegrationConfig(
            worker_config_dto.name, worker_config_dto.category, worker_config_dto.attributes)
        return integration_config


class IntegrationsAdapter():
    def __init__(self):
        self.integration_mapping = {
            "email": {
                "smpt": SMPTEmailIntegration
            }
        }

    def from_autoppia_backend(self, worker_config_dto):
        integrations = {}
        for integration in worker_config_dto.integration:
            integration_config: IntegrationConfig = IntegrationConfigAdapter().from_autoppia_backend(integration)
            integration_class: Integration = self.integration_mapping[integration_config.category][integration_config.name]
            integration:IntegrationInterface = integration_class(integration_config)
            integrations[integration_config.category][integration_config.name] = integration

        return integration
