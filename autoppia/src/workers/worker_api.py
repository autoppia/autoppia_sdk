from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Body
from fastapi.responses import JSONResponse, StreamingResponse
import json
import logging
import os
from werkzeug.utils import secure_filename
import uvicorn
import asyncio
from sse_starlette.sse import EventSourceResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerAPI")

class WorkerAPI:
    """
    HTTP server wrapper for worker implementations using FastAPI.
    
    This class provides an HTTP interface for worker operations including
    message processing with streaming capability.
    
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
        
        # File upload configuration
        self.upload_folder = os.path.join(os.getcwd(), 'uploads')
        self.max_content_length = 16 * 1024 * 1024  # 16MB max file size
        os.makedirs(self.upload_folder, exist_ok=True)

        # Register HTTP routes
        self.register_http_routes()

    def register_http_routes(self):
        """Register HTTP routes for the FastAPI app"""
        
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

        @self.app.post('/call')
        def handle_http_message(data: Dict[str, Any] = Body(...)):
            """Handle messages via HTTP POST, supporting both streaming and non-streaming responses"""
            logger.info("HTTP message request received")
            
            try:
                if not data:
                    raise HTTPException(status_code=400, detail="No JSON data provided")
            except Exception as e:
                logger.error(f"Invalid JSON received: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

            if not self.worker:
                logger.error("Worker not initialized")
                raise HTTPException(status_code=500, detail="Worker not initialized")

            message = data.get("message", "")
            logger.info(f"Received HTTP message: {message[:50]}...")

            # Check if streaming is requested
            stream_response = data.get("stream", False)

            if stream_response and hasattr(self.worker, 'call_stream'):
                async def event_generator():
                    try:
                        # Initial response
                        data = {"type": "response", "response": "Hello! I received your message"}
                        yield json.dumps(data)

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

                                return json.dumps(data)
                            except Exception as e:
                                logger.error(f"Error in send_message: {e}", exc_info=True)
                                error_data = {"type": "error", "error": str(e)}
                                return json.dumps(error_data)

                        # Call worker with streaming
                        result = self.worker.call_stream(message, lambda msg: (yield send_message(msg)))
                        
                        # Send completion
                        completion_data = {"type": "complete", "complete": True}
                        if result is not None:
                            completion_data["result"] = result
                        yield json.dumps(completion_data)

                    except Exception as e:
                        logger.error(f"Error in streaming worker call: {e}", exc_info=True)
                        error_data = {"type": "error", "error": str(e)}
                        yield json.dumps(error_data)

                return EventSourceResponse(
                    event_generator(),
                    media_type='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no',
                        'Connection': 'keep-alive'
                    }
                )
            else:
                # Non-streaming request
                try:
                    result = self.worker.call(message)
                    return JSONResponse({
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    logger.error(f"Error processing HTTP message: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail=str(e))

    def start(self):
        """Start the HTTP server using uvicorn"""
        logger.info("Starting worker...")
        self.worker.start()
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            workers=1,  # Single worker for SSE support
            timeout_keep_alive=65,
            access_log=True,
            loop="auto"
        )
        
        logger.info(f"Worker API server starting on http://{self.host}:{self.port}")
        server = uvicorn.Server(config)
        server.run()

    def stop(self):
        """Stop the HTTP server"""
        logger.info("Stopping worker API...")
        if self.worker:
            try:
                self.worker.stop()
                logger.info("Worker stopped")
            except Exception as e:
                logger.error(f"Error stopping worker: {e}")
        logger.info("Worker API stopped")
