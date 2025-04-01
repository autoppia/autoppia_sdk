from typing import Dict, Optional, List
from autoppia_backend_client.api.apps_config_api import AppsConfigApi
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
from autoppia_backend_client.models import WorkerConfig as WorkerConfigDTO
from autoppia_sdk.src.workers.worker_user_conf_service import WorkerUserConfService

config = Configuration()
config.host = "https://api.autoppia.com"
api_client = ApiClient(configuration=config)

class AppUserConfService(WorkerUserConfService):
    """Service class for managing app configurations.
    
    This class extends the WorkerUserConfService to provide additional functionality
    for retrieving app configurations and associated worker configurations.
    """

    def __init__(self):
        """Initialize the AppUserConfService with an API client."""
        super().__init__()
        self.apps_api = AppsConfigApi(self.api_client)
    
    def retrieve_app_config(self, app_id) -> WorkerConfigDTO:
        """Retrieve the configuration for a specific app.
        
        Args:
            app_id: The unique identifier of the app.
            
        Returns:
            WorkerConfigDTO: The app configuration data transfer object.
            
        Raises:
            ApiException: If there is an error communicating with the API.
        """
        app_config: WorkerConfigDTO = self.apps_api.apps_config_apps_read(app_id)
        return app_config
    
    def retrieve_app_workers(self, app_id) -> Dict[str, WorkerConfigDTO]:
        """Retrieve the configurations for all workers associated with an app.
        
        Args:
            app_id: The unique identifier of the app.
            
        Returns:
            Dict[str, WorkerConfigDTO]: Dictionary of worker configurations keyed by worker name.
            
        Raises:
            ApiException: If there is an error communicating with the API.
        """
        worker_configs = self.apps_api.apps_config_apps_workers_list(app_id)
        return {worker.name: worker for worker in worker_configs}
    
    def retrieve_app_worker(self, app_id, worker_name) -> Optional[WorkerConfigDTO]:
        """Retrieve the configuration for a specific worker associated with an app.
        
        Args:
            app_id: The unique identifier of the app.
            worker_name: The name of the worker to retrieve.
            
        Returns:
            Optional[WorkerConfigDTO]: The worker configuration data transfer object,
                or None if the worker is not found.
            
        Raises:
            ApiException: If there is an error communicating with the API.
        """
        worker_configs = self.retrieve_app_workers(app_id)
        return worker_configs.get(worker_name)
    
    def list_apps(self) -> List[WorkerConfigDTO]:
        """Retrieve a list of all available apps.
        
        Returns:
            List[WorkerConfigDTO]: List of app configurations.
            
        Raises:
            ApiException: If there is an error communicating with the API.
        """
        return self.apps_api.apps_config_apps_list()
