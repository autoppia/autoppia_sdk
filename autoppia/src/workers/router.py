import json
import logging
import requests
import time
import socketio
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from autoppia.src.workers.adapter import AIWorkerConfigAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerRouter")

class WorkerRouter():
    """A simplified router class for handling communication with AI workers via Socket.IO.

    This class manages the routing and communication with AI worker instances,
    using a clean and reliable event-driven approach.
    """
    
    def __init__(self, ip: str, port: int):
        """Initializes a WorkerRouter instance.

        Args:
            ip (str): The IP address of the worker.
            port (int): The port number the worker is listening on.
        """
        self.ip = ip
        self.port = port
        self.socketio_url = f"http://{self.ip}:{self.port}"
        self.timeout = 2400  # 40 minutes total timeout (increased from 30)
        self.ping_timeout = 1800  # 30 minutes ping timeout (matches server)
        self.connect_timeout = 600  # 10 minutes connect timeout (increased from 2)
        self._call_in_progress = False
        logger.info(f"Initialized WorkerRouter with SocketIO URL: {self.socketio_url}")
        logger.info(f"Timeouts: total={self.timeout}s, ping={self.ping_timeout}s, connect={self.connect_timeout}s")
    
    def call(self, message: str, stream_callback=None, keep_alive=False):
        """Sends a message to the worker for processing via Socket.IO.
        
        Args:
            message (str): The message to send to the worker
            stream_callback (callable, optional): Callback function to handle streaming responses
            keep_alive (bool, optional): If True, returns the connection for reuse
        
        Returns:
            The final result from the worker, or (result, connection) if keep_alive=True
        """
        # Prevent concurrent calls
        if self._call_in_progress:
            raise Exception("Another call is already in progress")
        
        self._call_in_progress = True
        sio = None
        
        try:
            # Create simplified Socket.IO client
            sio = self._create_socketio_client()
            
            # Track response state
            response_state = {
                'completed': False,
                'result': None,
                'error': None,
                'last_activity': time.time()
            }
            
            # Setup event handlers
            self._setup_event_handlers(sio, response_state, stream_callback)
            
            # Connect to server
            logger.info(f"Connecting to {self.socketio_url}...")
            sio.connect(self.socketio_url, wait_timeout=self.connect_timeout)
            logger.info("Connected successfully")
            
            # Send message
            sio.emit('message', {"message": message})
            logger.info(f"Message sent: {message[:50]}...")
            
            # Wait for completion
            self._wait_for_completion(sio, response_state)
            
            # Handle final result
            # if response_state['error']:
            #     raise Exception(f"Worker error: {response_state['error']}")
            
            if keep_alive:
                self._call_in_progress = False
                return response_state['result'], sio
            else:
                if sio.connected:
                    sio.disconnect()
                self._call_in_progress = False
                return response_state['result']
                
        except Exception as e:
            logger.error(f"Call failed: {e}")
            if sio and sio.connected:
                try:
                    sio.disconnect()
                except:
                    pass
            self._call_in_progress = False
            raise
    
    def _create_socketio_client(self):
        """Create a simplified Socket.IO client with proper timeout settings."""
        # Create HTTP session with appropriate timeouts
        session = requests.Session()
        retry_strategy = Retry(total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = (self.connect_timeout, self.timeout)  # Use configured timeouts
        
        return socketio.Client(
            reconnection=False,  # Disable auto-reconnection for simplicity
            logger=logger,
            engineio_logger=False,
            http_session=session
        )
    
    def _setup_event_handlers(self, sio, response_state, stream_callback):
        """Setup simplified event handlers."""
        
        @sio.event
        def connect():
            logger.info("Connected to Socket.IO server")
            logger.info(f"Connection established with server at {self.socketio_url}")
        
        @sio.event
        def disconnect():
            logger.info("Disconnected from Socket.IO server")
            logger.warning(f"Lost connection to server at {self.socketio_url}")
        
        @sio.on('message')
        def on_message(data):
            """Handle all streaming response messages."""
            response_state['last_activity'] = time.time()
            logger.debug(f"Received message from server: {str(data)[:100]}...")
            
            if not stream_callback:
                return
                
            try:
                # Simplified and robust message handling
                content = None
                
                if isinstance(data, dict):
                    # Dictionary message - extract content safely
                    content = data.get('stream') or data.get('text') or str(data)
                elif isinstance(data, str):
                    # String message - use directly
                    content = data
                else:
                    # Other types - convert to string
                    content = str(data)
                
                # Send content to callback if we have it
                if content:
                    stream_callback(content)
                    
            except Exception as e:
                logger.error(f"Error in stream callback: {e}")
                response_state['error'] = str(e)
                response_state['completed'] = True
        
        @sio.on('complete')
        def on_complete(data):
            """Handle completion signal."""
            response_state['last_activity'] = time.time()
            response_state['completed'] = True
            logger.info("Received completion signal from server")
            
            if isinstance(data, dict):
                response_state['result'] = data.get('result', '')
                if 'error' in data:
                    response_state['error'] = data['error']
                    logger.error(f"Server reported error: {data['error']}")
            else:
                response_state['result'] = str(data) if data else ''
            
            logger.info("Request completed successfully")
        
        @sio.on('error')
        def on_error(data):
            """Handle error messages."""
            response_state['last_activity'] = time.time()
            response_state['completed'] = True
            
            if isinstance(data, dict):
                error_msg = data.get('error', 'Unknown error')
            else:
                error_msg = str(data)
            
            response_state['error'] = error_msg
            logger.error(f"Worker error: {error_msg}")
        
        @sio.event
        def connect_error(data):
            logger.error(f"Connection error: {data}")
            response_state['error'] = f"Connection error: {data}"
            response_state['completed'] = True
        
        @sio.on('pong')
        def on_pong(data):
            """Handle pong responses from server"""
            response_state['last_activity'] = time.time()
            logger.debug(f"Received pong from server: {data}")
            # Don't mark as completed for pong messages
    
    def _wait_for_completion(self, sio, response_state):
        """Wait for the request to complete with timeout handling."""
        start_time = time.time()
        last_log_time = start_time
        
        logger.info(f"Waiting for completion with timeouts: total={self.timeout}s, ping={self.ping_timeout}s")
        
        while not response_state['completed']:
            if not sio.connected:
                logger.error("Connection lost during processing")
                raise Exception("Connection lost")
            
            current_time = time.time()
            elapsed = current_time - start_time
            since_activity = current_time - response_state['last_activity']
            
            # Log progress every 15 seconds (more frequent)
            if current_time - last_log_time > 15:
                logger.info(f"Still waiting... elapsed: {elapsed:.1f}s, since_activity: {since_activity:.1f}s, connected: {sio.connected}")
                last_log_time = current_time
                
                # Send heartbeat to server if no activity for 10 seconds
                if since_activity > 10:
                    try:
                        sio.emit('ping', {'timestamp': current_time})
                        logger.debug("Sent heartbeat ping to server")
                    except Exception as e:
                        logger.warning(f"Failed to send heartbeat: {e}")
            
            # Check total timeout
            if elapsed > self.timeout:
                logger.error(f"Request timeout after {self.timeout} seconds (total elapsed: {elapsed:.1f}s)")
                raise Exception(f"Request timeout after {self.timeout} seconds")
            
            # Check activity timeout (no messages received) - more lenient for long responses
            if since_activity > self.ping_timeout:
                logger.error(f"No activity timeout after {self.ping_timeout} seconds (since_activity: {since_activity:.1f}s)")
                raise Exception(f"No activity timeout after {self.ping_timeout} seconds")
            
            time.sleep(0.1)  # Small sleep to prevent busy waiting
        
        total_elapsed = time.time() - start_time
        logger.info(f"Request completed after {total_elapsed:.1f} seconds")
