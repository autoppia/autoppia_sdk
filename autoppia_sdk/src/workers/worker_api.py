from typing import Optional, Type

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from autoppia_sdk.src.standardization.workers.interfaces import AIWorker


class WorkerMessage(BaseModel):
    message: str


class WorkerAPI:
    def __init__(self, worker):
        self.app = FastAPI(title="WorkerAPI", description="API Wrapper for deployed worker")
        self.worker: AIWorker = worker

        # Register routes
        self.setup_routes()

    def setup_routes(self):
        @self.app.on_event("startup")
        async def startup_event():
            self.worker.start()

        @self.app.on_event("shutdown")
        async def shutdown_event():
            if self.worker:
                self.worker.stop()

        @self.app.post("/process")
        def process_message(message: WorkerMessage):
            if not self.worker:
                raise HTTPException(status_code=500, detail="Worker not initialized")

            try:
                result = self.worker.call(message.message)
                return {"result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "worker_type": self.worker_class.__name__}

    def get_app(self) -> FastAPI:
        return self.app
    
    @classmethod
    def from_worker_id(cls, worker_id, worker_class):
        worker = AIWorkerAdapter(worker_id).from_backend()
        return cls(worker)
