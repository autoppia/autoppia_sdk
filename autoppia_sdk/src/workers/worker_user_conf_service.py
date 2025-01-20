from autoppia_backend_client.api.workers_config_api import WorkersConfigApi
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
from autoppia_backend_client.models import WorkerConfig  as WorkerConfigDTO

config = Configuration()
config.host = "https://api.autoppia.com"
api_client = ApiClient(configuration=config)

class WorkerUserConfService:
    def __init__(self):
        self.api_client = api_client

    def retrieveWorker(self, worker_id) -> WorkerConfigDTO:
        workersApi = WorkersConfigApi(self.api_client)
        workerConfig: WorkerConfigDTO = workersApi.workers_config_workers_read(worker_id)
        return workerConfig
