from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
import logging
import os
from werkzeug.utils import secure_filename
import uvicorn
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerAPI")

class WorkerAPI:
    """
    WebSocket server wrapper for worker implementations using FastAPI.
    
    This class provides a WebSocket interface for worker operations including
    message processing with real-time communication.
    
    Attributes:
        worker: The worker instance that handles message processing
        app: The FastAPI application instance
    """
    def __init__(self, worker, host="localhost", port=8000):
        """
        Initialize the WorkerAPI.
        
        Args:
            worker: Worker instance that will process messages
            host (str): Host to bind the server to
            port (int): Port to listen on
        """
        self.worker = worker
        self.host = host
        self.port = port
        self.app = FastAPI(title="Worker API")
        self.active_connections: Dict[int, WebSocket] = {}
        
        # File upload configuration
        self.upload_folder = os.path.join(os.getcwd(), 'uploads')
        self.max_content_length = 16 * 1024 * 1024  # 16MB max file size
        os.makedirs(self.upload_folder, exist_ok=True)

        # Register routes
        self.register_routes()

    def register_routes(self):
        """Register WebSocket and HTTP routes for the FastAPI app"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Handle WebSocket connections"""
            await websocket.accept()
            connection_id = id(websocket)
            self.active_connections[connection_id] = websocket
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_json()
                    message = data.get("message", "")
                    logger.info(f"Received WebSocket message: {message[:50]}...")

                    if not self.worker:
                        await websocket.send_json({
                            "type": "error",
                            "error": "Worker not initialized"
                        })
                        continue

                    try:
                        # Send initial response
                        await websocket.send_json({
                            "type": "response",
                            "response": "Message received, processing..."
                        })

                        # Process message with streaming support
                        async def send_message(msg):
                            try:
                                if isinstance(msg, str):
                                    data = {"type": "stream", "stream": msg}
                                elif isinstance(msg, dict):
                                    if msg.get("type") == "text" and msg.get("role") == "assistant":
                                        data = {"type": "message", "message": msg}
                                    elif msg.get("type") == "task":
                                        data = {
                                            "type": "tool",
                                            "tool": {
                                                "title": msg.get("title", ""),
                                                "text": msg.get("text", ""),
                                                "icon": msg.get("icon", False)
                                            }
                                        }
                                    else:
                                        data = {"type": "stream", "stream": str(msg)}
                                else:
                                    data = {"type": "stream", "stream": str(msg)}

                                await websocket.send_json(data)
                            except Exception as e:
                                logger.error(f"Error in send_message: {e}", exc_info=True)
                                await websocket.send_json({
                                    "type": "error",
                                    "error": str(e)
                                })

                        # Call worker with streaming
                        if hasattr(self.worker, 'call_stream'):
                            result = await self.worker.call_stream(message, send_message)
                        else:
                            result = await self.worker.call(message)
                            await send_message(result)

                        # Send completion
                        await websocket.send_json({
                            "type": "complete",
                            "complete": True,
                            "result": result
                        })

                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        await websocket.send_json({
                            "type": "error",
                            "error": str(e)
                        })

            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {connection_id}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}", exc_info=True)
            finally:
                self.active_connections.pop(connection_id, None)

        @self.app.post('/upload')
        async def upload_file(files: list[UploadFile] = File(...)):
            """Handle file uploads via HTTP POST"""
            logger.info("File upload request received")
            
            if not files:
                logger.warning("No files provided")
                raise HTTPException(status_code=400, detail="No files provided")
            
            uploaded_files = []
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(self.upload_folder, filename)
                    
                    # Save file
                    try:
                        contents = await file.read()
                        with open(filepath, 'wb') as f:
                            f.write(contents)
                        logger.info(f"File saved: {filepath}")
                        uploaded_files.append(filename)
                        
                        if hasattr(self.worker, 'file_uploaded'):
                            try:
                                await self.worker.file_uploaded(filepath)
                            except Exception as e:
                                logger.error(f"Error processing uploaded file with worker: {e}", exc_info=True)
                    except Exception as e:
                        logger.error(f"Error saving file: {e}", exc_info=True)
                        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
            
            return JSONResponse({
                'success': True,
                'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
                'files': uploaded_files
            })

    def start(self):
        """Start the WebSocket server using uvicorn"""
        logger.info("Starting worker...")
        self.worker.start()
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            workers=1,  # Single worker for WebSocket support
            timeout_keep_alive=65,
            access_log=True,
            loop="auto"
        )
        
        logger.info(f"Worker API server starting on ws://{self.host}:{self.port}/ws")
        server = uvicorn.Server(config)
        server.run()

    def stop(self):
        """Stop the WebSocket server"""
        logger.info("Stopping worker API...")
        if self.worker:
            try:
                self.worker.stop()
                logger.info("Worker stopped")
            except Exception as e:
                logger.error(f"Error stopping worker: {e}")
        logger.info("Worker API stopped")
