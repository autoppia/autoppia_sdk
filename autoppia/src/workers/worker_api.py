from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
import logging
import os
import time
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerAPI")


class WorkerAPI:
    """
    Simplified WebSocket server wrapper for worker implementations using Flask-SocketIO.
    
    This class provides a clean WebSocket interface for worker operations with
    simplified message processing and reliable connection handling.
    
    Attributes:
        worker: The worker instance that handles message processing
        socketio: The Flask-SocketIO server instance
        app: The Flask application instance
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
        self.app = Flask(__name__)
        
        # Configure Socket.IO with appropriate settings
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            ping_timeout=1800,  # 30 minutes ping timeout (increased from 20)
            ping_interval=30,   # Send ping every 30 seconds (decreased from 1 minute for more frequent checks)
            logger=logger,
            engineio_logger=False,
            # Additional Engine.IO timeout settings
            http_compression=False,  # Disable compression to reduce processing overhead
            allow_upgrades=True,     # Allow WebSocket upgrades
            transports=['websocket', 'polling'],  # Prefer WebSocket but allow fallback
            # Engine.IO specific timeouts
            max_http_buffer_size=1000000,  # 1MB buffer for large responses
            always_connect=True,     # Always try to connect
            # Additional settings for long-running operations
            async_mode='threading',  # Use threading for better performance
            # Add additional timeout configurations
            socket_timeout=1800,  # 30 minutes socket timeout
            heartbeat_timeout=1800,  # 30 minutes heartbeat timeout
            heartbeat_interval=30,  # 30 seconds heartbeat interval
            # Engine.IO specific settings for stability
            engineio_client_timeout=1800,  # 30 minutes Engine.IO timeout
            transport_timeout=1800,  # 30 minutes transport timeout
            connection_timeout=180,  # 3 minutes connection timeout
            # Force keep connection alive
            force_new_connection=False,  # Reuse connections
            reconnection_attempts=5,  # Allow reconnection attempts
        )
        
        self._running = False
        self.active_connections = set()
        self.processing_clients = set()  # Track clients currently processing
        
        # File upload configuration
        self.app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Register event handlers and routes
        self._register_event_handlers()
        self._register_http_routes()

    def _register_http_routes(self):
        """Register HTTP routes for the Flask app"""
        
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            """Handle file uploads via HTTP POST"""
            logger.info(f"File upload request received from {request.remote_addr}")
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
                
            files = request.files.getlist('file')
            
            if not files or files[0].filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            uploaded_files = []
            for file in files:
                if file:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    logger.info(f"File saved: {filepath}")
                    uploaded_files.append(filename)
                    
                    # Notify worker if it has file handling capability
                    if hasattr(self.worker, 'file_uploaded'):
                        try:
                            self.worker.file_uploaded(filepath)
                        except Exception as e:
                            logger.error(f"Error processing uploaded file: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
                'files': uploaded_files
            })

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'active_connections': len(self.active_connections),
                'processing_clients': len(self.processing_clients),
                'server_running': self._running,
                'worker_status': 'active' if self.worker else 'inactive'
            })

        @self.app.route('/status', methods=['GET'])
        def server_status():
            """Detailed server status endpoint"""
            return jsonify({
                'server': {
                    'running': self._running,
                    'host': self.host,
                    'port': self.port,
                    'timestamp': time.time()
                },
                'connections': {
                    'active': len(self.active_connections),
                    'processing': len(self.processing_clients),
                    'connection_ids': list(self.active_connections)
                },
                'worker': {
                    'available': self.worker is not None,
                    'has_streaming': hasattr(self.worker, 'call_stream'),
                    'has_file_upload': hasattr(self.worker, 'file_uploaded')
                },
                'socket_config': {
                    'ping_timeout': 1800,
                    'ping_interval': 30,
                    'max_buffer_size': 1000000
                }
            })

    def _register_event_handlers(self):
        """Register Socket.IO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect(auth=None):
            """Handle new client connections"""
            client_id = request.sid
            self.active_connections.add(client_id)
            logger.info(f"Client connected: {client_id} from {request.environ.get('REMOTE_ADDR', 'unknown')}. Total connections: {len(self.active_connections)}")
            
            # Send welcome message to confirm connection
            self.socketio.emit('message', {
                "stream": "🔗 Connection established. Ready to process your requests."
            }, room=client_id)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnections"""
            client_id = request.sid
            self.active_connections.discard(client_id)
            was_processing = client_id in self.processing_clients
            self.processing_clients.discard(client_id)
            logger.info(f"Client disconnected: {client_id} (was_processing: {was_processing}). Total connections: {len(self.active_connections)}")
            
            # Log disconnect reason if available
            disconnect_reason = request.environ.get('disconnect_reason', 'unknown')
            if disconnect_reason != 'unknown':
                logger.info(f"Disconnect reason for {client_id}: {disconnect_reason}")

        @self.socketio.on('ping')
        def handle_ping(data):
            """Handle ping/heartbeat messages from clients"""
            client_id = request.sid
            logger.debug(f"Received ping from {client_id}")
            
            # Respond with pong to confirm connection health
            self.socketio.emit('pong', {
                'timestamp': data.get('timestamp') if data else time.time(),
                'server_time': time.time()
            }, room=client_id)
            
            logger.debug(f"Sent pong response to {client_id}")

        @self.socketio.on('message')
        def handle_message(data):
            """Handle messages from clients - simplified and reliable"""
            client_id = request.sid
            
            try:
                # Parse message data
                if not isinstance(data, dict):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from {client_id}: {e}")
                        emit('error', {"error": f"Invalid JSON: {str(e)}"})
                        return
                
                # Validate worker
                if not self.worker:
                    logger.error("Worker not initialized")
                    emit('error', {"error": "Worker not initialized"})
                    return
                
                # Check if client is already processing
                if client_id in self.processing_clients:
                    logger.warning(f"Client {client_id} already processing, ignoring duplicate message")
                    return
                
                message = data.get("message", "")
                logger.info(f"Processing message from {client_id}: {message[:50]}...")
                
                # Mark client as processing
                self.processing_clients.add(client_id)
                
                try:
                    # Send initial acknowledgment
                    emit('message', {"stream": "Processing your request..."})
                    
                    # Process message based on worker capabilities
                    if hasattr(self.worker, 'call_stream'):
                        self._handle_streaming_call(client_id, message)
                    else:
                        self._handle_simple_call(client_id, message)
                        
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}", exc_info=True)
                    emit('error', {"error": str(e)})
                    emit('complete', {"result": "", "error": str(e)})
                    
                finally:
                    # Always remove from processing set
                    self.processing_clients.discard(client_id)
                    
            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {e}", exc_info=True)
                try:
                    emit('error', {"error": str(e)})
                except:
                    pass
                finally:
                    self.processing_clients.discard(client_id)

    def _handle_streaming_call(self, client_id, message):
        """Handle streaming worker call"""
        import threading
        import time
        
        # Keep-alive mechanism
        keep_alive_active = True
        last_activity = time.time()
        
        def keep_alive_worker():
            """Send periodic keep-alive messages to prevent connection timeout"""
            nonlocal last_activity  # Declare nonlocal at the top
            
            while keep_alive_active:
                try:
                    current_time = time.time()
                    # Send keep-alive if no activity for 15 seconds (more aggressive)
                    if current_time - last_activity > 15:
                        self.socketio.emit('message', {"stream": "⏳ Processing..."}, room=client_id)
                        logger.debug(f"Sent keep-alive to {client_id}")
                        # Update activity after sending keep-alive
                        last_activity = current_time
                    time.sleep(15)  # Check every 15 seconds (more frequent)
                except Exception as e:
                    logger.error(f"Keep-alive error for {client_id}: {e}")
                    break
        
        # Start keep-alive thread
        keep_alive_thread = threading.Thread(target=keep_alive_worker, daemon=True)
        keep_alive_thread.start()
        
        def send_chunk(chunk):
            """Send message chunk to client"""
            nonlocal last_activity
            last_activity = time.time()  # Update activity timestamp
            
            try:
                if isinstance(chunk, str):
                    # Simple string message
                    self.socketio.emit('message', {"stream": chunk}, room=client_id)
                elif isinstance(chunk, dict):
                    # Structured message
                    if chunk.get("type") == "text":
                        self.socketio.emit('message', {"stream": chunk.get("text", "")}, room=client_id)
                    elif chunk.get("type") == "task":
                        # Tool/task message
                        self.socketio.emit('message', {
                            "stream": f"[TOOL] {chunk.get('title', '')}: {chunk.get('text', '')}"
                        }, room=client_id)
                    else:
                        # Generic dict message
                        self.socketio.emit('message', {"stream": str(chunk)}, room=client_id)
                else:
                    # Other types
                    self.socketio.emit('message', {"stream": str(chunk)}, room=client_id)
                    
            except Exception as e:
                logger.error(f"Error sending chunk to {client_id}: {e}")
                raise  # Re-raise to stop processing
        
        try:
            # Call worker with streaming
            logger.info(f"Starting streaming call for {client_id}")
            result = self.worker.call_stream(message, send_chunk)
            
            # Send completion
            self.socketio.emit('complete', {
                "result": result if result is not None else "",
                "complete": True
            }, room=client_id)
            
            logger.info(f"Streaming call completed for {client_id}")
                
        finally:
            # Stop keep-alive thread
            keep_alive_active = False

    def _handle_simple_call(self, client_id, message):
        """Handle simple (non-streaming) worker call"""
        logger.info(f"Starting simple call for {client_id}")
        result = self.worker.call(message)
        
        # Send result as completion
        self.socketio.emit('complete', {
            "result": result if result is not None else "",
            "complete": True
        }, room=client_id)
        
        logger.info(f"Simple call completed for {client_id}")

    def start(self):
        """Start the WebSocket server"""
        logger.info("Starting worker API...")
        self._running = True
        
        # Start worker
        if hasattr(self.worker, 'start'):
            self.worker.start()
            logger.info("Worker started")
        
        # Start Socket.IO server
        logger.info(f"Starting Socket.IO server on http://{self.host}:{self.port}")
        self.socketio.run(
            self.app, 
            host=self.host, 
            port=self.port,
            debug=False,
            use_reloader=False,
            log_output=True,
            allow_unsafe_werkzeug=True
        )

    def stop(self):
        """Stop the WebSocket server"""
        logger.info("Stopping worker API...")
        self._running = False
        
        # Stop worker
        if self.worker and hasattr(self.worker, 'stop'):
            try:
                self.worker.stop()
                logger.info("Worker stopped")
            except Exception as e:
                logger.error(f"Error stopping worker: {e}")
        
        # Stop Socket.IO server
        try:
            self.socketio.stop()
            logger.info("Socket.IO server stopped")
        except Exception as e:
            logger.error(f"Error stopping Socket.IO server: {e}")
        
        logger.info("Worker API stopped")
