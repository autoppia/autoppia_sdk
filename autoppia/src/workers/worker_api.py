import asyncio
import websockets
import json
import logging
import time
import uuid
from typing import Optional, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor

from .models import MessageType, WebSocketMessage
from ..utils.api_key import ApiKeyVerifier
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerAPI")


class ClientConnection:
    """Represents a connected client with state management"""
    
    def __init__(self, websocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.connected_at = time.time()
        self.last_activity = time.time()
        self.is_processing = False
        self.message_count = 0
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
    
    async def send_message(self, message: WebSocketMessage):
        """Send message to client with error handling"""
        try:
            await self.websocket.send(message.to_json())
            self.message_count += 1
            logger.debug(f"Sent message to {self.client_id}: {message.type.value}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Client {self.client_id} connection closed while sending message")
            raise
        except Exception as e:
            logger.error(f"Error sending message to {self.client_id}: {e}")
            raise
    
    async def send_stream(self, content: str, stream_id: str = None):
        """Send streaming content to client"""
        message = WebSocketMessage(
            type=MessageType.STREAM,
            id=stream_id or str(uuid.uuid4()),
            data={"content": content}
        )
        await self.send_message(message)
    
    async def send_complete(self, result: str, error: str = None):
        """Send completion message to client"""
        message = WebSocketMessage(
            type=MessageType.COMPLETE,
            id=str(uuid.uuid4()),
            data={"result": result, "error": error}
        )
        await self.send_message(message)
    
    async def send_error(self, error: str):
        """Send error message to client"""
        message = WebSocketMessage(
            type=MessageType.ERROR,
            id=str(uuid.uuid4()),
            data={"error": error}
        )
        await self.send_message(message)


class WorkerAPI:
    """
    Professional WebSocket server for AI worker implementations.
    
    Features:
    - Native WebSocket support with high performance
    - Streaming responses for AI workers
    - Automatic connection management and heartbeat
    - Clean, structured message format
    - Comprehensive error handling
    - Simple API for easy integration
    """
    
    def __init__(self, worker, host: str = "localhost", port: int = 8000, api_base_url: Optional[str] = "https://api.autoppia.com"):
        """
        Initialize the WorkerAPI.
        
        Args:
            worker: Worker instance that processes messages
            host: Host to bind the server to
            port: Port to listen on
        """
        self.worker = worker
        self.host = host
        self.port = port
        self.clients: Dict[str, ClientConnection] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 300  # 5 minutes
        self.is_running = False
        # Always require API key regardless of passed value
        self.require_api_key = True
        # Always initialize verifier since API key is always required
        self.api_verifier = ApiKeyVerifier(base_url=api_base_url)
        
        logger.info(f"WorkerAPI initialized on {host}:{port}")
        logger.info(f"Heartbeat interval: {self.heartbeat_interval}s, Connection timeout: {self.connection_timeout}s")
    
    async def start(self):
        """Start the WebSocket server"""
        logger.info("Starting WebSocket server...")
        self.is_running = True
        
        # Start worker if it has a start method
        if hasattr(self.worker, 'start'):
            await asyncio.get_event_loop().run_in_executor(self.executor, self.worker.start)
            logger.info("Worker started")
        
        # Start heartbeat task
        asyncio.create_task(self._heartbeat_task())
        
        # Start server
        async with websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=60,
            close_timeout=10,
            max_size=50 * 1024 * 1024  # 50MB max message size
        ):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            logger.info("Server ready to accept connections")
            
            # Keep server running
            while self.is_running:
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the WebSocket server"""
        logger.info("Stopping WebSocket server...")
        self.is_running = False
        
        # Disconnect all clients
        for client in list(self.clients.values()):
            try:
                await client.websocket.close()
            except:
                pass
        
        self.clients.clear()
        
        # Stop worker
        if hasattr(self.worker, 'stop'):
            await asyncio.get_event_loop().run_in_executor(self.executor, self.worker.stop)
            logger.info("Worker stopped")
        
        self.executor.shutdown(wait=True)
        logger.info("WebSocket server stopped")
    
    async def _handle_client(self, websocket, path):
        """Handle new client connections"""
        # API key verification (header: x-api-key or query param: api_key)
        if self.require_api_key:
            api_key = None
            try:
                headers = getattr(websocket, 'request_headers', None)
                if headers:
                    api_key = headers.get('x-api-key') or headers.get('X-API-Key')
                if not api_key and path:
                    parsed = urlparse(path)
                    qs = parse_qs(parsed.query)
                    values = qs.get('api_key')
                    api_key = values[0] if values else None
            except Exception as e:
                logger.error(f"Error extracting API key: {e}")
            
            if not api_key:
                logger.warning("Missing API key. Closing connection.")
                try:
                    await websocket.close(code=4401, reason="API key required")
                finally:
                    return
            
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.executor, self.api_verifier.verify_api_key, api_key)
                if not result or not result.get('is_valid'):
                    logger.warning("Invalid API key. Closing connection.")
                    try:
                        await websocket.close(code=4403, reason="Invalid API key")
                    finally:
                        return
            except Exception as e:
                logger.error(f"API key verification error: {e}")
                try:
                    await websocket.close(code=1011, reason="Verification error")
                finally:
                    return

        client_id = str(uuid.uuid4())
        client = ClientConnection(websocket, client_id)
        self.clients[client_id] = client
        
        logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        try:
            # Send welcome message
            await client.send_message(WebSocketMessage(
                type=MessageType.CONNECT,
                id=str(uuid.uuid4()),
                data={"message": "Connection established. Ready to process requests."}
            ))
            
            # Handle client messages
            async for message in websocket:
                try:
                    await self._process_message(client, message)
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
                    await client.send_error(f"Message processing error: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected normally")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client
            if client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"Client {client_id} cleaned up. Active connections: {len(self.clients)}")
    
    async def _process_message(self, client: ClientConnection, raw_message: str):
        """Process incoming message from client"""
        client.update_activity()
        
        try:
            message = WebSocketMessage.from_json(raw_message)
            logger.debug(f"Received {message.type.value} from {client.client_id}")
            
            if message.type == MessageType.MESSAGE:
                await self._handle_worker_message(client, message)
            elif message.type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(client, message)
            else:
                logger.warning(f"Unknown message type: {message.type.value}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {client.client_id}: {e}")
            await client.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message from {client.client_id}: {e}")
            await client.send_error(f"Processing error: {str(e)}")
    
    async def _handle_worker_message(self, client: ClientConnection, message: WebSocketMessage):
        """Handle message processing by worker"""
        if client.is_processing:
            await client.send_error("Another message is already being processed")
            return
        
        if not self.worker:
            await client.send_error("Worker not available")
            return
            
        client.is_processing = True
        content = message.data.get("content", "")
        
        logger.info(f"Processing message from {client.client_id}: {content[:50]}...")
        
        try:
            # Check if worker supports streaming
            if hasattr(self.worker, 'call_stream'):
                await self._handle_streaming_worker(client, content, message.id)
            else:
                await self._handle_simple_worker(client, content, message.id)
        
        except Exception as e:
            logger.error(f"Worker error for {client.client_id}: {e}")
            await client.send_complete("", str(e))
        finally:
            client.is_processing = False
    
    async def _handle_streaming_worker(self, client: ClientConnection, content: str, message_id: str):
        """Handle streaming worker response"""
        
        def stream_callback(chunk):
            """Callback for streaming chunks"""
            # Convert chunk to string format
            if isinstance(chunk, dict):
                if chunk.get("type") == "text":
                    return chunk.get("text", "")
                elif chunk.get("type") == "task":
                    return f"[TOOL] {chunk.get('title', '')}: {chunk.get('text', '')}"
                else:
                    return str(chunk)
            else:
                return str(chunk)
        
        # Run worker in executor to avoid blocking
        def worker_task():
            chunks = []
            
            def collect_chunk(chunk):
                processed = stream_callback(chunk)
                if processed:
                    chunks.append(processed)
            
            try:
                result = self.worker.call_stream(content, collect_chunk)
                return result, chunks
            except Exception as e:
                logger.error(f"Streaming worker error: {e}")
                raise
        
        try:
            # Execute worker task
            result, chunks = await asyncio.get_event_loop().run_in_executor(
                self.executor, worker_task
            )
            
            # Send all chunks
            for chunk in chunks:
                await client.send_stream(chunk, message_id)
            
            # Send completion
            await client.send_complete(result or "", None)
            
            logger.info(f"Streaming completed for {client.client_id} ({len(chunks)} chunks)")
                
        except Exception as e:
            logger.error(f"Streaming error for {client.client_id}: {e}")
            await client.send_complete("", str(e))
    
    async def _handle_simple_worker(self, client: ClientConnection, content: str, message_id: str):
        """Handle simple worker response"""
        try:
            # Run worker in executor
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.worker.call, content
            )
            
            await client.send_complete(result or "", None)
            logger.info(f"Simple worker completed for {client.client_id}")
            
        except Exception as e:
            logger.error(f"Simple worker error for {client.client_id}: {e}")
            await client.send_complete("", str(e))
    
    async def _handle_heartbeat(self, client: ClientConnection, message: WebSocketMessage):
        """Handle heartbeat message"""
        response = WebSocketMessage(
            type=MessageType.HEARTBEAT,
            id=message.id,
            data={"status": "alive", "timestamp": time.time()}
        )
        await client.send_message(response)
    
    async def _heartbeat_task(self):
        """Background task to monitor client connections"""
        while self.is_running:
            try:
                current_time = time.time()
                disconnected_clients = []
                
                for client_id, client in self.clients.items():
                    # Check for timeout
                    if current_time - client.last_activity > self.connection_timeout:
                        logger.warning(f"Client {client_id} timed out")
                        disconnected_clients.append(client_id)
                        try:
                            await client.websocket.close()
                        except:
                            pass
                
                # Clean up disconnected clients
                for client_id in disconnected_clients:
                    if client_id in self.clients:
                        del self.clients[client_id]
                
                if len(self.clients) > 0:
                    logger.debug(f"Active connections: {len(self.clients)}")
                
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
            
            await asyncio.sleep(self.heartbeat_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status information"""
        return {
            "server": {
                "running": self.is_running,
                "host": self.host,
                "port": self.port,
                "uptime": time.time() - (self.clients[list(self.clients.keys())[0]].connected_at if self.clients else time.time())
            },
            "connections": {
                "active": len(self.clients),
                "processing": sum(1 for c in self.clients.values() if c.is_processing),
                "total_messages": sum(c.message_count for c in self.clients.values())
            },
            "worker": {
                "available": self.worker is not None,
                "supports_streaming": hasattr(self.worker, 'call_stream')
            }
        }


# Convenience function for easy server startup
async def start_worker_server(worker, host="localhost", port=8000):
    """Start a worker server with the given worker instance"""
    api = WorkerAPI(worker, host, port)
    await api.start()
    return api
