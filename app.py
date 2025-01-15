from workers.deployment.workers_api import WorkerAPI
from email_worker.email_worker import EmailAgent
import os


def get_app():

    worker_id = os.getenv("WORKER_ID", None)

    if not worker_id:
        raise Exception("Worker ID not set")

    worker = AIWorkerAdapter().create_worker_from_id(worker_id)
    api = WorkerAPI(worker=worker)
    app = api.get_app()
    return app


app = get_app()
