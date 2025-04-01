from typing import Dict, Optional, Any, Set
import socketio
import json
import logging
import threading
from autoppia_sdk.src.workers.worker_api import WorkerAPI
from autoppia_sdk.src.apps.interface import AIApp
from autoppia_sdk.src.workers.interface import AIWorker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AppAPI")


class AppAPI(WorkerAPI):
    """
    WebSocket server wrapper for app implementations using Python-SocketIO.
    
    This class extends the WorkerAPI to provide additional functionality for
    handling app-specific operations, including routing messages to specific
    workers within the app.
    
    Attributes:
        app: The app instance that handles message processing
        sio: The SocketIO server instance
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
        
        # Register additional event handlers for app-specific operations
        self.sio.on('get_app_info', self.handle_get_app_info)
        self.sio.on('get_ui_config', self.handle_get_ui_config)
        self.sio.on('get_workers', self.handle_get_workers)
    
    def handle_message(self, sid, data):
        """Handle messages from clients with worker routing"""
        client_id = sid
        
        try:
            if not isinstance(data, dict):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    self.sio.emit('error', {"error": f"Invalid JSON: {str(e)}"}, room=client_id)
                    return
            
            if not self.app:
                logger.error("App not initialized")
                self.sio.emit('error', {"error": "App not initialized"}, room=client_id)
                return
            
            # Check if this is an action request
            if "action" in data:
                action = data.get("action")
                
                if action == "get_app_info":
                    self.handle_get_app_info(sid, data)
                    return
                elif action == "get_ui_config":
                    self.handle_get_ui_config(sid, data)
                    return
                elif action == "get_workers":
                    self.handle_get_workers(sid, data)
                    return
            
            # Extract message and optional worker name
            message = data.get("message", "")
            worker_name = data.get("worker")
            
            logger.info(f"Received message from {client_id}: {message[:50]}...")
            if worker_name:
                logger.info(f"Routing to worker: {worker_name}")
            
            # Acknowledge receipt
            self.sio.emit('response', {"response": "Hello! I received your message"}, room=client_id)
            
            # Check if the app supports streaming
            if hasattr(self.app, 'call_stream'):
                def send_message(msg):
                    """Synchronous message sending wrapper"""
                    logger.info(f"Sending message via send_message: {str(msg)[:100]}...")
                    
                    try:
                        self._send_message_sync(client_id, msg)
                    except Exception as e:
                        logger.error(f"Error in send_message: {e}", exc_info=True)
                
                # Use streaming call with sync sending
                logger.info("Starting streaming call")
                result = self.app.call_stream(message, send_message, worker_name) if worker_name else self.app.call_stream(message, send_message)
                
                # Send completion message
                try:
                    if result is not None:
                        self.sio.emit('complete', {"complete": True, "result": result}, room=client_id)
                    else:
                        self.sio.emit('complete', {"complete": True}, room=client_id)
                    logger.info("Streaming call completed")
                except Exception as e:
                    logger.error(f"Error sending completion message: {e}")
            else:
                # Fallback to non-streaming call
                logger.info("Starting non-streaming call")
                result = self.app.route_message(message, worker_name) if worker_name else self.app.call(message)
                self.sio.emit('result', {"result": result}, room=client_id)
                logger.info("Non-streaming call completed")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            try:
                self.sio.emit('error', {"error": str(e)}, room=client_id)
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    def handle_get_app_info(self, sid, data):
        """Handle requests for app information"""
        client_id = sid
        
        try:
            if not self.app:
                logger.error("App not initialized")
                self.sio.emit('error', {"error": "App not initialized"}, room=client_id)
                return
            
            app_info = self.app.get_app_info()
            self.sio.emit('app_info', {"app_info": app_info}, room=client_id)
            logger.info("Sent app info")
        except Exception as e:
            logger.error(f"Error getting app info: {e}", exc_info=True)
            try:
                self.sio.emit('error', {"error": str(e)}, room=client_id)
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    def handle_get_ui_config(self, sid, data):
        """Handle requests for UI configuration"""
        client_id = sid
        
        try:
            if not self.app:
                logger.error("App not initialized")
                self.sio.emit('error', {"error": "App not initialized"}, room=client_id)
                return
            
            ui_config = self.app.get_ui_config()
            self.sio.emit('ui_config', {"ui_config": ui_config}, room=client_id)
            logger.info("Sent UI config")
        except Exception as e:
            logger.error(f"Error getting UI config: {e}", exc_info=True)
            try:
                self.sio.emit('error', {"error": str(e)}, room=client_id)
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
    
    def handle_get_workers(self, sid, data):
        """Handle requests for worker information"""
        client_id = sid
        
        try:
            if not self.app:
                logger.error("App not initialized")
                self.sio.emit('error', {"error": "App not initialized"}, room=client_id)
                return
            
            workers = self.app.get_workers()
            worker_info = {name: {"name": name} for name in workers.keys()}
            self.sio.emit('workers', {"workers": worker_info}, room=client_id)
            logger.info(f"Sent worker info for {len(worker_info)} workers")
        except Exception as e:
            logger.error(f"Error getting workers: {e}", exc_info=True)
            try:
                self.sio.emit('error', {"error": str(e)}, room=client_id)
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")
