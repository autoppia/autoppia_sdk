from dataclasses import dataclass
from typing import Dict, Any, Type
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.integrations.implementations.base import Integration
from autoppia_sdk.src.integrations.implementations.email.smtp_integration import SMPTEmailIntegration

@dataclass(frozen=True)
class IntegrationConfig:
    """Immutable configuration container for integration instances."""
    name: str
    category: str
    attributes: Dict[str, Any]

class IntegrationConfigAdapter:
    """Adapter for converting backend DTOs to IntegrationConfig objects."""
    
    @staticmethod
    def from_autoppia_backend(worker_config_dto) -> IntegrationConfig:
        """Convert backend integration DTO to IntegrationConfig.
        
        Args:
            worker_config_dto: Source data transfer object from backend
            
        Returns:
            IntegrationConfig: Validated configuration object
            
        Raises:
            ValueError: If required attributes are missing
        """
        if not worker_config_dto.integration_obj:
            raise ValueError("Integration configuration requires an integration object")

        attributes = {}
        for attr in worker_config_dto.user_integration_attributes:
            # Prefer credential value if available
            value = attr.credential_obj.credential if attr.credential_obj else attr.value
            if not attr.integration_attribute_obj:
                raise ValueError(f"Missing attribute definition for {attr.name}")
            attributes[attr.integration_attribute_obj.name] = value

        return IntegrationConfig(
            name=worker_config_dto.integration_obj.name,
            category=worker_config_dto.integration_obj.category,
            attributes=attributes
        )

class IntegrationsAdapter:
    """Factory for creating integration instances from backend configurations."""
    
    def __init__(self) -> None:
        self.integration_mapping: Dict[str, Dict[str, Type[Integration]]] = {
            "email": {"Smtp": SMPTEmailIntegration}
        }

    def from_autoppia_backend(self, worker_config_dto) -> Dict[str, Dict[str, IntegrationInterface]]:
        """Create integration instances from backend DTO.
        
        Args:
            worker_config_dto: Source data transfer object from backend
            
        Returns:
            Nested dictionary of integration instances organized by category and name
            
        Raises:
            KeyError: If integration type isn't registered in the mapping
        """
        integrations: Dict[str, Dict[str, IntegrationInterface]] = {}

        for integration in worker_config_dto.user_integration:
            if not integration.integration_obj:
                continue  # Skip invalid entries

            category = integration.integration_obj.category
            config = IntegrationConfigAdapter.from_autoppia_backend(integration)
            
            try:
                integration_class = self.integration_mapping[config.category][config.name]
            except KeyError:
                raise KeyError(f"No integration registered for {config.category}/{config.name}")

            integrations.setdefault(category, {})[config.name] = integration_class(config.attributes)

        return integrations
