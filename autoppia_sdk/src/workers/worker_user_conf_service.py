from autoppia_backend_client.api.workers_config_api import WorkersConfigApi
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
from autoppia_backend_client.models import WorkerConfig  as WorkerConfigDTO

config = Configuration()
config.host = "https://api.autoppia.com"
api_client = ApiClient(configuration=config)

class WorkerUserConfService:
    """Service class for managing worker configurations.
    
    This class provides functionality to interact with worker configurations
    through the Autoppia API client.
    """

    def __init__(self):
        """Initialize the WorkerUserConfService with an API client."""
        self.api_client = api_client

    def retrieve_worker_config(self, worker_id) -> WorkerConfigDTO:
        """Retrieve the configuration for a specific worker.
        
        Args:
            worker_id: The unique identifier of the worker.
            
        Returns:
            WorkerConfigDTO: The worker configuration data transfer object.
            
        Raises:
            ApiException: If there is an error communicating with the API.
        """
        workersApi = WorkersConfigApi(self.api_client)
        workerConfig: WorkerConfigDTO = workersApi.workers_config_workers_read(worker_id)
        return workerConfig
