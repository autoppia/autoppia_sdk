from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from autoppia_sdk.src.workers.implementations.ai_worker import AIWorker


class WorkerMessage(BaseModel):
    message: str


class WorkerAPI:
    def __init__(self, worker: AIWorker):
        self.app = FastAPI(title="Worker API", description="API Wrapper for the worker")
        self.worker: Optional[AIWorker] = worker

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
            return {"status": "healthy", "worker_type": self.worker.__class__.__name__}

    def get_app(self) -> FastAPI:
        return self.app
