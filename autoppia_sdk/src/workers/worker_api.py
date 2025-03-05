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
            WebSocket endpoint for processing messages with streaming support.
            
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
                        
                        # Check if the worker supports streaming
                        if hasattr(self.worker, 'call_stream'):
                            # Define a callback function to send streaming messages
                            async def send_streaming_message(msg):
                                try:
                                    # Format the message based on its type
                                    if isinstance(msg, str):
                                        await websocket.send_json({"stream": msg})
                                    elif isinstance(msg, dict):
                                        # Handle different message types
                                        if msg.get("type") == "text" and msg.get("role") == "assistant":
                                            await websocket.send_json({"stream": msg.get("text", "")})
                                        elif msg.get("type") == "task":
                                            # For tool execution messages
                                            await websocket.send_json({
                                                "tool": {
                                                    "title": msg.get("title", ""),
                                                    "text": msg.get("text", ""),
                                                    "icon": msg.get("icon", False)
                                                }
                                            })
                                        else:
                                            # For other message types
                                            await websocket.send_json({"stream": str(msg)})
                                except Exception as e:
                                    print(f"Error sending streaming message: {e}")
                            
                            # Use streaming call
                            self.worker.call_stream(message, send_streaming_message)
                            
                            # Send completion message
                            await websocket.send_json({"complete": True})
                        else:
                            # Fallback to non-streaming call
                            result = self.worker.call(message)
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
