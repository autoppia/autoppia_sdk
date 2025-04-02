from typing import Dict, Optional, Any, Set
import json
import logging
import threading
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from autoppia_sdk.src.workers.worker_api import WorkerAPI
from autoppia_sdk.src.apps.interface import AIApp
from autoppia_sdk.src.workers.interface import AIWorker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AppAPI")


class AppAPI(WorkerAPI):
    """
    FastAPI server wrapper for app implementations.
    
    This class extends the WorkerAPI to provide additional functionality for
    handling app-specific operations, including routing messages to specific
    workers within the app.
    
    Attributes:
        app: The app instance that handles message processing
        api: The FastAPI instance
        active_connections: Dictionary of active WebSocket connections
    """
    def __init__(self, app: AIApp, host="localhost", port=8000):
        """
        Initialize the AppAPI.
        
        Args:
            app: App instance that will process messages
            host (str): Host to bind the server to
            port (int): Port to listen on
        """
        super().__init__(worker=app, host=host, port=port)
        self.app = app  # Store a reference to the app for app-specific operations
        self.api = FastAPI()
        self.active_connections = {}
        
        # Register HTTP endpoints
        self.api.get("/app_info")(self.handle_get_app_info_http)
        self.api.get("/ui_config")(self.handle_get_ui_config_http)
        self.api.get("/workers")(self.handle_get_workers_http)
        
        # Register WebSocket endpoint
        self.api.websocket("/ws")(self.websocket_endpoint)
    
    async def websocket_endpoint(self, websocket: WebSocket):
        """Handle WebSocket connections and messages"""
        await websocket.accept()
        client_id = str(id(websocket))
        self.active_connections[client_id] = websocket
        
        try:
            while True:
                data = await websocket.receive_text()
                # Process the message asynchronously
                asyncio.create_task(self.handle_message(client_id, data))
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected")
            if client_id in self.active_connections:
                del self.active_connections[client_id]
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            if client_id in self.active_connections:
                del self.active_connections[client_id]
    
    async def handle_message(self, client_id, data):
        """Handle messages from clients with worker routing"""
        try:
            if not isinstance(data, dict):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    await self._send_message(client_id, "error", {"error": f"Invalid JSON: {str(e)}"})
                    return
            
            if not self.app:
                logger.error("App not initialized")
                await self._send_message(client_id, "error", {"error": "App not initialized"})
                return
            
            # Check if this is an action request
            if "action" in data:
                action = data.get("action")
                
                if action == "get_app_info":
                    await self.handle_get_app_info_ws(client_id, data)
                    return
                elif action == "get_ui_config":
                    await self.handle_get_ui_config_ws(client_id, data)
                    return
                elif action == "get_workers":
                    await self.handle_get_workers_ws(client_id, data)
                    return
            
            # Extract message and optional worker name
            message = data.get("message", "")
            worker_name = data.get("worker")
            
            logger.info(f"Received message from {client_id}: {message[:50]}...")
            if worker_name:
                logger.info(f"Routing to worker: {worker_name}")
            
            # Acknowledge receipt
            await self._send_message(client_id, "response", {"response": "Hello! I received your message"})
            
            # Check if the app supports streaming
            if hasattr(self.app, 'call_stream'):
                async def send_message(msg):
                    """Asynchronous message sending wrapper"""
                    logger.info(f"Sending message via send_message: {str(msg)[:100]}...")
                    
                    try:
                        await self._send_message(client_id, "stream", {"content": msg})
                    except Exception as e:
                        logger.error(f"Error in send_message: {e}", exc_info=True)
                
                # Use streaming call with async sending
                logger.info("Starting streaming call")
                result = await self._run_in_thread(
                    self.app.call_stream, message, send_message, worker_name if worker_name else None
                )
                
                # Send completion message
                try:
                    if result is not None:
                        await self._send_message(client_id, "complete", {"complete": True, "result": result})
                    else:
                        await self._send_message(client_id, "complete", {"complete": True})
                    logger.info("Streaming call completed")
                except Exception as e:
                    logger.error(f"Error sending completion message: {e}")
            else:
                # Fallback to non-streaming call
                logger.info("Starting non-streaming call")
                if worker_name:
                    result = await self._run_in_thread(self.app.route_message, message, worker_name)
                else:
                    result = await self._run_in_thread(self.app.call, message)
                await self._send_message(client_id, "result", {"result": result})
                logger.info("Non-streaming call completed")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            try:
                await self._send_message(client_id, "error", {"error": str(e)})
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    async def _send_message(self, client_id, event_type, data):
        """Send a message to a client via WebSocket"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            message = {"type": event_type, "data": data}
            await websocket.send_text(json.dumps(message))
    
    async def _run_in_thread(self, func, *args, **kwargs):
        """Run a blocking function in a thread pool"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    # HTTP endpoint handlers
    async def handle_get_app_info_http(self, request: Request):
        """HTTP endpoint for app information"""
        try:
            if not self.app:
                raise HTTPException(status_code=500, detail="App not initialized")
            
            app_info = self.app.get_app_info()
            return {"app_info": app_info}
        except Exception as e:
            logger.error(f"Error getting app info: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def handle_get_ui_config_http(self, request: Request):
        """HTTP endpoint for UI configuration"""
        try:
            if not self.app:
                raise HTTPException(status_code=500, detail="App not initialized")
            
            ui_config = self.app.get_ui_config()
            return {"ui_config": ui_config}
        except Exception as e:
            logger.error(f"Error getting UI config: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def handle_get_workers_http(self, request: Request):
        """HTTP endpoint for worker information"""
        try:
            if not self.app:
                raise HTTPException(status_code=500, detail="App not initialized")
            
            workers = self.app.get_workers()
            worker_info = {name: {"name": name} for name in workers.keys()}
            return {"workers": worker_info}
        except Exception as e:
            logger.error(f"Error getting workers: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    # WebSocket event handlers
    async def handle_get_app_info_ws(self, client_id, data):
        """WebSocket handler for app information"""
        try:
            if not self.app:
                logger.error("App not initialized")
                await self._send_message(client_id, "error", {"error": "App not initialized"})
                return
            
            app_info = self.app.get_app_info()
            await self._send_message(client_id, "app_info", {"app_info": app_info})
            logger.info("Sent app info")
        except Exception as e:
            logger.error(f"Error getting app info: {e}", exc_info=True)
            try:
                await self._send_message(client_id, "error", {"error": str(e)})
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    async def handle_get_ui_config_ws(self, client_id, data):
        """WebSocket handler for UI configuration"""
        try:
            if not self.app:
                logger.error("App not initialized")
                await self._send_message(client_id, "error", {"error": "App not initialized"})
                return
            
            ui_config = self.app.get_ui_config()
            await self._send_message(client_id, "ui_config", {"ui_config": ui_config})
            logger.info("Sent UI config")
        except Exception as e:
            logger.error(f"Error getting UI config: {e}", exc_info=True)
            try:
                await self._send_message(client_id, "error", {"error": str(e)})
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    async def handle_get_workers_ws(self, client_id, data):
        """WebSocket handler for worker information"""
        try:
            if not self.app:
                logger.error("App not initialized")
                await self._send_message(client_id, "error", {"error": "App not initialized"})
                return
            
            workers = self.app.get_workers()
            worker_info = {name: {"name": name} for name in workers.keys()}
            await self._send_message(client_id, "workers", {"workers": worker_info})
            logger.info(f"Sent worker info for {len(worker_info)} workers")
        except Exception as e:
            logger.error(f"Error getting workers: {e}", exc_info=True)
            try:
                await self._send_message(client_id, "error", {"error": str(e)})
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    def start(self):
        """Start the FastAPI server"""
        logger.info(f"Starting FastAPI server on {self.host}:{self.port}")
        uvicorn.run(self.api, host=self.host, port=self.port)
