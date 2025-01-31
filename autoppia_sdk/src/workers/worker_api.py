from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class WorkerMessage(BaseModel):
    """
    Pydantic model for worker message requests.
    
    Attributes:
        message (str): The message to be processed by the worker
    """
    message: str

class WorkerAPI:
    """
    FastAPI wrapper for worker implementations.
    
    This class provides a REST API interface for worker operations including
    health checks and message processing.
    
    Attributes:
        app (FastAPI): The FastAPI application instance
        worker: The worker instance that handles message processing
    """
    def __init__(self, worker):
        """
        Initialize the WorkerAPI.
        
        Args:
            worker: Worker instance that will process messages
        """
        self.app = FastAPI(title="Worker API", description="API Wrapper for the worker")
        self.worker = worker

        # Register routes
        self.setup_routes()

    def setup_routes(self):
        """
        Configure API routes and event handlers.
        
        Sets up the following endpoints:
        - POST /process: Process a message
        - GET /health: Check worker health
        
        And event handlers:
        - startup: Starts the worker
        - shutdown: Stops the worker
        """
        @self.app.on_event("startup")
        async def startup_event():
            self.worker.start()

        @self.app.on_event("shutdown")
        async def shutdown_event():
            if self.worker:
                self.worker.stop()

        @self.app.post("/process")
        def process_message(message: WorkerMessage):
            """
            Process a message using the worker.
            
            Args:
                message (WorkerMessage): The message to process
                
            Returns:
                dict: Contains the processing result
                
            Raises:
                HTTPException: If worker is not initialized or processing fails
            """
            if not self.worker:
                raise HTTPException(status_code=500, detail="Worker not initialized")

            try:
                result = self.worker.call(message.message)
                return {"result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health_check():
            """
            Check the health status of the worker.
            
            Returns:
                dict: Contains status and worker type information
            """
            return {"status": "healthy", "worker_type": self.worker.__class__.__name__}

    def get_app(self) -> FastAPI:
        """
        Get the FastAPI application instance.
        
        Returns:
            FastAPI: The configured FastAPI application
        """
        return self.app
