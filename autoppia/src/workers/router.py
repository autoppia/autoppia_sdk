import asyncio
import websockets
import json
import logging
import time
import uuid
from typing import Optional, Callable, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading
import os
import jwt
from dotenv import load_dotenv
import requests
from .models import MessageType, WebSocketMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerRouter")

load_dotenv()

class ConnectionState:
    """Track connection state and response handling"""
    
    def __init__(self):
        self.connected = False
        self.processing = False
        self.result = None
        self.error = None
        self.completed = False
        self.last_activity = time.time()
        self.message_count = 0
        self.stream_callback = None
        self.connection_id = None
    
    def reset_for_new_request(self):
        """Reset state for a new request"""
        self.processing = False
        self.result = None
        self.error = None
        self.completed = False
        self.message_count = 0
        self.update_activity()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()


class WorkerRouter:
    """
    Professional WebSocket client for communicating with AI workers.
    
    Features:
    - Native WebSocket with automatic reconnection
    - Streaming response support
    - Robust error handling and timeout management
    - Clean, structured message format
    - Thread-safe operation
    - Simple API for easy integration
    """
    
    def __init__(self, ip: str, port: int, api_key: Optional[str] = None, bearer_token: Optional[str] = None, template_id: Optional[str] = None):
        """
        Initialize the WorkerRouter.

        Args:
            ip: IP address of the worker server
            port: Port number of the worker server
        """
        self.ip = ip
        self.port = port
        self.url = f"ws://{ip}:{port}"
        self.state = ConnectionState()
        self.websocket = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.event_loop = None
        self.loop_thread = None
        self._lock = threading.Lock()
        self.api_key = api_key
        self.bearer_token = bearer_token
        
        # Configuration
        self.connect_timeout = 30  # seconds
        self.response_timeout = 3600  # 60 minutes
        self.heartbeat_interval = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.template_id = template_id #worker_id
        
        logger.info(f"WorkerRouter initialized for {self.url}")
        logger.info(f"Timeouts: connect={self.connect_timeout}s, response={self.response_timeout}s")
        logger.info(f"Retries: max={self.max_retries}, delay={self.retry_delay}s")
    
    def call(self, message: str, stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Send a message to the worker and wait for response.
        
        Args:
            message: The message to send
            stream_callback: Optional callback for streaming responses
        
        Returns:
            The worker's response
            
        Raises:
            Exception: If the call fails after all retries
        """
        with self._lock:
            if self.state.processing:
                raise Exception("Another call is already in progress")
            
            self.state.processing = True
        
        try:
            userId = self.authenticatedCookie(self.bearer_token)
            result = self.reduceUserBalance(userId, self.template_id)
            if result:
                return self._call_with_retry(message, stream_callback)
            else:
                return ""
        finally:
            with self._lock:
                self.state.processing = False

    def authenticatedCookie(self, bear_token):
        authorization_header = bear_token
        access_token = (
            authorization_header.replace("Bearer ", "")
            if authorization_header
            else None
        )

        # Validate the access token (e.g., using a library like PyJWT)
        if not access_token:
            return None

        try:
            decoded_token = jwt.decode(
                access_token,
                key=os.getenv("SIGNING_KEY"),
                algorithms=os.getenv("ALGORITHM"),
            )
            userId = decoded_token["userId"]
            return userId
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        
    def reduceUserBalance(self, userId, template_id):
        response = requests.post(os.getenv("REDUCE_BALANCE_ENDPOINT"), json={
            "userId": userId,
            "template_id": template_id
        })

        if response.status_code == 200:
            result = response.json()
            return result["success"]
        else:
            return False

    
    def _call_with_retry(self, message: str, stream_callback: Optional[Callable[[str], None]]) -> str:
        """Execute call with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to process message")
                return self._execute_call(message, stream_callback)
                    
            except Exception as e:
                last_exception = e
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                self._cleanup_connection()
        
        raise Exception(f"All {self.max_retries} attempts failed. Last error: {last_exception}")
    
    def _execute_call(self, message: str, stream_callback: Optional[Callable[[str], None]]) -> str:
        """Execute a single call attempt"""
        # Start event loop in background thread if not running
        self._ensure_event_loop()
        
        # Reset state for new request
        self.state.reset_for_new_request()
        self.state.stream_callback = stream_callback
        
        # Execute the async call
        future = asyncio.run_coroutine_threadsafe(
            self._async_call(message),
            self.event_loop
        )
        
        return future.result(timeout=self.response_timeout + 60)  # Add buffer to async timeout
    
    def _ensure_event_loop(self):
        """Ensure event loop is running in background thread"""
        if self.event_loop is None or not self.event_loop.is_running():
            if self.loop_thread and self.loop_thread.is_alive():
                self.loop_thread.join(timeout=5)
            
            self.event_loop = asyncio.new_event_loop()
            self.loop_thread = threading.Thread(
                target=self._run_event_loop,
                daemon=True
            )
            self.loop_thread.start()
            
            # Wait for loop to start
            while not self.event_loop.is_running():
                time.sleep(0.1)
    
    def _run_event_loop(self):
        """Run the event loop in background thread"""
        asyncio.set_event_loop(self.event_loop)
        try:
            self.event_loop.run_forever()
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            self.event_loop = None
    
    async def _async_call(self, message: str) -> str:
        """Async implementation of the call"""
        try:
            # Connect to server
            await self._connect()
            
            # Send message
            await self._send_message(message)
            
            # Wait for response
            return await self._wait_for_response()
            
        except Exception as e:
            logger.error(f"Async call failed: {e}")
            raise
        finally:
            await self._disconnect()
    
    async def _connect(self):
        """Connect to the WebSocket server"""
        if self.websocket and not self.websocket.closed:
            return
        
        logger.info(f"Connecting to {self.url}...")
        
        try:
            connect_kwargs = {
                "ping_interval": 20,
                "ping_timeout": 60,
                "close_timeout": 10,
                "max_size": 50 * 1024 * 1024,
            }
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"
            if headers:
                connect_kwargs["extra_headers"] = headers

            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    self.url,
                    **connect_kwargs
                ),
                timeout=self.connect_timeout
            )
            
            self.state.connected = True
            self.state.update_activity()
            logger.info("Connected successfully")
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            
        except asyncio.TimeoutError:
            raise Exception(f"Connection timeout after {self.connect_timeout} seconds")
        except Exception as e:
            raise Exception(f"Connection failed: {e}")
    
    async def _disconnect(self):
        """Disconnect from the WebSocket server"""
        if self.websocket and not self.websocket.closed:
            try:
                await self.websocket.close()
                logger.info("Disconnected from server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        
        self.state.connected = False
        self.websocket = None
    
    async def _send_message(self, content: str):
        """Send message to server"""
        if not self.websocket or self.websocket.closed:
            raise Exception("Not connected to server")
        
        message = WebSocketMessage(
            type=MessageType.MESSAGE,
            id=str(uuid.uuid4()),
            data={"content": content}
        )
        
        await self.websocket.send(message.to_json())
        logger.info(f"Message sent: {content[:50]}...")
    
    async def _handle_messages(self):
        """Handle incoming messages from server"""
        try:
            async for raw_message in self.websocket:
                try:
                    message = WebSocketMessage.from_json(raw_message)
                    await self._process_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
            self.state.connected = False
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            self.state.connected = False
    
    async def _process_message(self, message: WebSocketMessage):
        """Process incoming message based on type"""
        self.state.update_activity()
        self.state.message_count += 1
        
        logger.debug(f"Received {message.type.value} (#{self.state.message_count})")
        
        if message.type == MessageType.CONNECT:
            logger.info("Connection confirmed by server")
            self.state.connection_id = message.id
        
        elif message.type == MessageType.STREAM:
            content = message.data.get("content", "")
            if self.state.stream_callback and content:
                try:
                    self.state.stream_callback(content)
                except Exception as e:
                    logger.error(f"Stream callback error: {e}")
        
        elif message.type == MessageType.COMPLETE:
            self.state.result = message.data.get("result", "")
            self.state.error = message.data.get("error")
            self.state.completed = True
            logger.info(f"Request completed (processed {self.state.message_count} messages)")
        
        elif message.type == MessageType.ERROR:
            self.state.error = message.data.get("error", "Unknown error")
            self.state.completed = True
            logger.error(f"Server error: {self.state.error}")
        
        elif message.type == MessageType.HEARTBEAT:
            # Echo heartbeat if needed
            pass
    
    async def _wait_for_response(self) -> str:
        """Wait for response with timeout"""
        start_time = time.time()
        
        logger.info(f"Waiting for response (timeout: {self.response_timeout}s)")
        
        while not self.state.completed:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Check connection
            if not self.state.connected or (self.websocket and self.websocket.closed):
                raise Exception("Connection lost during response wait")
            
            # Check timeout
            if elapsed > self.response_timeout:
                raise Exception(f"Response timeout after {self.response_timeout} seconds")
            
            # Check activity timeout (no messages received)
            since_activity = current_time - self.state.last_activity
            activity_timeout = min(300, self.response_timeout / 2)  # 5 minutes or half response timeout
            
            if since_activity > activity_timeout:
                raise Exception(f"No activity timeout after {activity_timeout} seconds")
            
            await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        logger.info(f"Response received after {total_time:.1f}s")
        
        # Handle errors
        if self.state.error:
            raise Exception(f"Worker error: {self.state.error}")
        
        return self.state.result or ""
    
    def _cleanup_connection(self):
        """Clean up connection state"""
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._disconnect(),
                self.event_loop
            )
        
        self.state.connected = False
        self.state.completed = False
    
    def close(self):
        """Close the router and clean up resources"""
        logger.info("Closing WorkerRouter...")
        
        self._cleanup_connection()
        
        if self.event_loop and self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        
        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        logger.info("WorkerRouter closed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get router status information"""
        return {
            "connection": {
                "url": self.url,
                "connected": self.state.connected,
                "processing": self.state.processing,
                "connection_id": self.state.connection_id
            },
            "activity": {
                "last_activity": self.state.last_activity,
                "message_count": self.state.message_count,
                "has_stream_callback": self.state.stream_callback is not None
            },
            "configuration": {
                "connect_timeout": self.connect_timeout,
                "response_timeout": self.response_timeout,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay
            }
        }


# Convenience function for quick worker calls
def call_worker(ip: str, port: int, message: str, stream_callback: Optional[Callable[[str], None]] = None) -> str:
    """
    Quick function to call a worker without managing router instance.
    
    Args:
        ip: Worker IP address
        port: Worker port
        message: Message to send
        stream_callback: Optional streaming callback
        
    Returns:
        Worker response
    """
    router = WorkerRouter(ip, port)
    try:
        return router.call(message, stream_callback)
    finally:
        router.close()
