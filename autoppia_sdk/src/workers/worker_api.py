from typing import Optional, Dict, Any, Set
import socketio
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import eventlet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerAPI")


class WorkerAPI:
    """
    WebSocket server wrapper for worker implementations using Python-SocketIO.
    
    This class provides a WebSocket interface for worker operations including
    message processing with synchronous sending capability.
    
    Attributes:
        worker: The worker instance that handles message processing
        sio: The SocketIO server instance
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
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.executor = ThreadPoolExecutor()
        self._running = False
        self.active_connections = set()  # Track active connections

        # Register event handlers
        self.sio.on('connect', self.handle_connect)
        self.sio.on('disconnect', self.handle_disconnect)
        self.sio.on('message', self.handle_message)
        self.sio.on('ping', self.handle_ping)
        
        # Set up heartbeat task
        self.setup_heartbeat()

    def handle_connect(self, sid, environ, auth=None):
        """Handle new client connections"""
        client_id = sid
        self.active_connections.add(client_id)
        logger.info(f"New client connected: {client_id}. Active connections: {len(self.active_connections)}")

    def handle_disconnect(self, sid):
        """Handle client disconnections"""
        client_id = sid
        if client_id in self.active_connections:
            self.active_connections.remove(client_id)
        logger.info(f"Client disconnected: {client_id}. Active connections: {len(self.active_connections)}")

    def handle_ping(self, sid):
        """Handle ping events"""
        return {'pong': True}

    def handle_message(self, sid, data):
        """Handle messages from clients"""
        client_id = sid
        
        try:
            if not isinstance(data, dict):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    self.sio.emit('error', {"error": f"Invalid JSON: {str(e)}"}, room=client_id)
                    return
            
            if not self.worker:
                logger.error("Worker not initialized")
                self.sio.emit('error', {"error": "Worker not initialized"}, room=client_id)
                return
            
            message = data.get("message", "")
            logger.info(f"Received message from {client_id}: {message[:50]}...")
            
            # Acknowledge receipt
            self.sio.emit('response', {"response": "Hello! I received your message"}, room=client_id)
            
            # Check if the worker supports streaming
            if hasattr(self.worker, 'call_stream'):
                def send_message(msg):
                    """Synchronous message sending wrapper"""
                    logger.info(f"Sending message via send_message: {str(msg)[:100]}...")
                    
                    try:
                        self._send_message_sync(client_id, msg)
                    except Exception as e:
                        logger.error(f"Error in send_message: {e}", exc_info=True)
                
                # Use streaming call with sync sending
                logger.info("Starting streaming call")
                result = self.worker.call_stream(message, send_message)
                
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
                result = self.worker.call(message)
                self.sio.emit('result', {"result": result}, room=client_id)
                logger.info("Non-streaming call completed")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            try:
                self.sio.emit('error', {"error": str(e)}, room=client_id)
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")

    def _send_message_sync(self, client_id, msg):
        """Synchronous function to send a message to the client"""
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} not in active connections, cannot send message")
            return
        
        try:
            # Format the message based on its type
            if isinstance(msg, str):
                # For string messages, just send as stream
                self.sio.emit('stream', {"stream": msg}, room=client_id)
                logger.debug(f"Sent string message: {msg[:50]}...")
            elif isinstance(msg, dict):
                # For dict messages, format based on type
                if msg.get("type") == "text" and msg.get("role") == "assistant":
                    # Send the full message
                    self.sio.emit('message', msg, room=client_id)
                    logger.debug(f"Sent assistant text message: {msg.get('text', '')[:50]}...")
                elif msg.get("type") == "task":
                    # Format tool/task messages
                    tool_msg = {
                        "tool": {
                            "title": msg.get("title", ""),
                            "text": msg.get("text", ""),
                            "icon": msg.get("icon", False)
                        }
                    }
                    self.sio.emit('tool', tool_msg, room=client_id)
                    logger.debug(f"Sent task message: {msg.get('title', '')}")
                else:
                    # Default case for other dict messages
                    self.sio.emit('stream', {"stream": str(msg)}, room=client_id)
                    logger.debug(f"Sent generic dict message")
                
            # Add a debug confirmation after successful sending
            logger.info(f"Message successfully sent to client {client_id} (type: {type(msg).__name__})")
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            logger.error(f"Failed message details: {str(msg)[:200]}")
            if client_id in self.active_connections:
                self.active_connections.remove(client_id)
            logger.info(f"Removed problematic client {client_id}. Active connections: {len(self.active_connections)}")

    def setup_heartbeat(self):
        """Set up a heartbeat event to keep connections alive"""
        def send_heartbeats():
            """Background task to send heartbeats to all clients"""
            while self._running:
                for client_id in list(self.active_connections):
                    try:
                        self.sio.emit('heartbeat', {"heartbeat": True}, room=client_id)
                        logger.debug(f"Heartbeat sent to {client_id}")
                    except Exception as e:
                        logger.warning(f"Failed to send heartbeat to {client_id}: {e}")
                threading.Event().wait(30)  # Wait for 30 seconds

        self.heartbeat_thread = threading.Thread(target=send_heartbeats)
        self.heartbeat_thread.daemon = True

    def start(self):
        """Start the WebSocket server"""
        self._running = True
        self.worker.start()
        logger.info("Worker started")
        
        # Start the heartbeat thread
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread started")
        
        # Run the server
        logger.info(f"Worker API server starting on http://{self.host}:{self.port}")
        eventlet.wsgi.server(eventlet.listen((self.host, self.port)), self.app)

    def stop(self):
        """Stop the WebSocket server"""
        logger.info("Stopping worker API...")
        self._running = False
        
        if self.worker:
            try:
                self.worker.stop()
                logger.info("Worker stopped")
            except Exception as e:
                logger.error(f"Error stopping worker: {e}")
        
        try:
            self.executor.shutdown(wait=False)
            logger.info("Executor shutdown")
        except Exception as e:
            logger.error(f"Error shutting down executor: {e}")
        
        logger.info("Worker API stopped")
