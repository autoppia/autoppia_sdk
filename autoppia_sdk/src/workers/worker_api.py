from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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
    
    This class provides a WebSocket interface for worker operations including
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
        Configure API routes, WebSocket endpoints, and event handlers.
        
        Sets up the following:
        - WebSocket /ws: WebSocket endpoint for message processing
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

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """
            WebSocket endpoint for processing messages.
            
            Args:
                websocket (WebSocket): The WebSocket connection
            """
            await websocket.accept()
            
            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_json()
                    
                    if not self.worker:
                        await websocket.send_json({"error": "Worker not initialized"})
                        continue
                    
                    try:
                        # Process the message
                        message = data.get("message", "")
                        result = self.worker.call(message)
                        
                        # Send result back to client
                        await websocket.send_json({"result": result})
                    except Exception as e:
                        await websocket.send_json({"error": str(e)})
            except WebSocketDisconnect:
                # Handle client disconnect
                pass

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
