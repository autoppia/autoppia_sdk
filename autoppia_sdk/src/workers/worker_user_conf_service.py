from autoppia_backend_client.api.workers_api import WorkersApi
from autoppia_backend_client.api.coworkers_api import CoworkersApi
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
from autoppia_backend_client.models import Worker as WorkerDTO, Coworker as CoworkerDTO

config = Configuration()
config.host = "https://api.autoppia.com"
api_client = ApiClient(configuration=config)


class WorkerUserConfService:
    def __init__(self):
        self.api_client = api_client

    def retrieveWorker(self, worker_id) -> WorkerDTO:
        workersApi = WorkersApi(self.api_client)
        worker: WorkerDTO = workersApi.workers_configuration_worker_read(worker_id)
        return worker


class CoworkerUserConfService:
    def __init__(self):
        self.api_client = api_client

    def retrieveCoworker(self, coworker_id) -> CoworkerDTO:
        coworkersApi = CoworkersApi(self.api_client)
        coworker: CoworkerDTO = coworkersApi.coworkers_configuration_coworkers_read(coworker_id)
        return coworker
