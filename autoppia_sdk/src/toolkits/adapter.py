from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO

from autoppia_sdk.src.toolkits.interface import UserToolkit


class UserToolkitAdapter:
    """
    Adapter class that converts UserToolkitDTO (backend data transfer object) to UserToolkit domain model.
    
    This adapter handles the transformation of complex nested DTO structures into a simplified
    UserToolkit model, including the extraction of toolkit configurations, integrations, and files.
    """

    def __init__(self, user_toolkit_dto):
        """
        Initialize the UserToolkitAdapter.

        Args:
            user_toolkit_dto (UserToolkitDTO): The data transfer object from the backend
                containing user toolkit configuration.
        """
        self.user_toolkit_dto: UserToolkitDTO = user_toolkit_dto
        self.user_toolkit: UserToolkit = UserToolkit(toolkit_name="", context={})

    def from_backend(self) -> UserToolkit:
        """
        Convert the backend DTO to a UserToolkit domain model.

        This method processes:
        - Basic toolkit information (name, instruction)
        - Configuration attributes
        - Integration attributes and credentials
        - Associated file IDs

        Returns:
            UserToolkit: The converted domain model containing simplified toolkit configuration.
        """
        self.user_toolkit.toolkit_name = (
            self.user_toolkit_dto.user_toolkit.toolkit_obj.name
        )
        self.user_toolkit.instruction = self.user_toolkit_dto.instruction

        self.user_toolkit.context = {}

        for attr in self.user_toolkit_dto.user_configuration_attributes:
            self.user_toolkit.context[attr.toolkit_attribute_obj.name] = attr.value

        for integration in self.user_toolkit_dto.user_configuration_linked_integrations:
            integration_obj = integration.user_integration
            for attr in integration_obj.user_integration_attributes:
                self.user_toolkit.context[attr.integration_attribute_obj.name] = (
                    attr.value
                    if attr.value
                    else (
                        attr.credential_obj.credential
                        if attr.credential_obj and attr.credential_obj.credential
                        else attr.document
                    )
                )

        file_ids = []

        for file in self.user_toolkit_dto.user_configuration_extra_files:
            file_ids.append(file.document.open_ai_id)

        self.user_toolkit.context_files = file_ids

        return self.user_toolkit
