from autoppia_backend_client.models import ListUserConfiguration as UserToolkitDTO

from autoppia_sdk.src.standardization.toolkits.interfaces import UserToolkit


class UserToolkitAdapter:
    def __init__(self, user_toolkit_dto):
        self.user_toolkit_dto: UserToolkitDTO = user_toolkit_dto
        self.user_toolkit: UserToolkit = UserToolkit(toolkit_name="", context={})

    def from_backend(self) -> UserToolkit:
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
