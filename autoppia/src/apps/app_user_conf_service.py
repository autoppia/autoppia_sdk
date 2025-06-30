from autoppia_backend_client.api.app_config_api import AppConfigApi
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
from autoppia_backend_client.models import AppConfig  as AppConfigDTO

config = Configuration()
config.host = "https://api.autoppia.com"
api_client = ApiClient(configuration=config)

class AppUserConfService:
    """Service class for managing app configurations.
    
    This class provides functionality to interact with app configurations
    through the Autoppia API client.
    """

    def __init__(self):
        """Initialize the AppUserConfService with an API client."""
        self.api_client = api_client

    def retrieve_app_config(self, app_id) -> AppConfigDTO:
        """Retrieve the configuration for a specific app.
        
        Args:
            app_id: The unique identifier of the app.
            
        Returns:
            AppConfigDTO: The app configuration data transfer object.
            
        Raises:
            ApiException: If there is an error communicating with the API.
        """
        appConfigApi = AppConfigApi(self.api_client)
        appConfig: AppConfigDTO = appConfigApi.app_config_app_read(app_id)
        return appConfig
