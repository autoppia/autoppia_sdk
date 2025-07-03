import json
import logging
import websockets
import asyncio
import requests
import time
from typing import Optional, Callable, Any
from websockets.legacy.client import WebSocketClientProtocol

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerRouter")

class WorkerRouter():
    """A router class for handling communication with AI workers via WebSocket.

    This class manages the routing and communication with AI worker instances,
    handling configuration retrieval and message processing through WebSocket.
    """

    @classmethod
    def from_id(cls, worker_id: int):
        """Fetches worker IP and port from the info endpoint"""
        try:
            payload = {
                "SECRET": "ekwklrklkfewf3232nm",
                "id": worker_id
            }
            logger.info(f"Fetching worker info for worker_id: {worker_id}")
            response = requests.get("http://3.251.99.81/info", json=payload)
            data = response.json()
            logger.info(f"Received worker info: {data}")
            ip = data.get("ip")
            port = data.get("port")
            
            if not ip or not port:
                logger.error(f"Invalid response: missing ip or port. Response: {data}")
                raise ValueError("Invalid response: missing ip or port")
                
            return cls(ip, port)
        except Exception as e:
            logger.error(f"Failed to fetch worker info: {str(e)}")
            raise Exception(f"Failed to fetch worker info: {str(e)}")
    
    def __init__(self, ip: str, port: int):
        """Initializes a WorkerRouter instance.

        Args:
            ip (str): The IP address of the worker.
            port (int): The port number the worker is listening on.
        """
        self.ip = ip
        self.port = port
        self.ws_url = f"ws://{self.ip}:{self.port}/ws"
        self.http_url = f"http://{self.ip}:{self.port}"
        logger.info(f"Initialized WorkerRouter with WebSocket URL: {self.ws_url}")
        self._websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False

    @property
    def websocket(self) -> Optional[WebSocketClientProtocol]:
        return self._websocket

    @websocket.setter
    def websocket(self, value: Optional[WebSocketClientProtocol]) -> None:
        self._websocket = value

    async def connect(self) -> None:
        """Establishes WebSocket connection with the worker."""
        if not self.connected:
            try:
                self._websocket = await websockets.connect(self.ws_url)
                self.connected = True
                logger.info("WebSocket connection established")
            except Exception as e:
                logger.error(f"Failed to establish WebSocket connection: {str(e)}")
                raise

    async def disconnect(self) -> None:
        """Closes the WebSocket connection."""
        if self.websocket and self.connected:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {str(e)}")
            finally:
                self._websocket = None
                self.connected = False
                logger.info("WebSocket connection closed")

    async def call(self, message: str, stream_callback: Optional[Callable[[Any], None]] = None) -> Any:
        """Sends a message to the worker for processing via WebSocket.
        
        Args:
            message (str): The message to send to the worker
            stream_callback (callable, optional): Callback function to handle streaming responses
        
        Returns:
            The final result from the worker
        """
        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                # Ensure connection is established
                if not self.connected:
                    await self.connect()

                if not self.websocket:
                    raise Exception("WebSocket connection not established")

                # Send message
                await self.websocket.send(json.dumps({"message": message}))
                logger.info(f"Message sent: {message[:50]}...")

                # Process responses
                final_result = None
                while True:
                    try:
                        response = await self.websocket.recv()
                        data = json.loads(response)
                        event_type = data.get("type")

                        if event_type == "error":
                            error_msg = data.get("error", "Unknown error")
                            logger.error(f"Worker returned error: {error_msg}")
                            raise Exception(f"Worker error: {error_msg}")

                        elif event_type == "complete":
                            final_result = data.get("result", data.get("complete", None))
                            logger.info("Received complete event")
                            return final_result

                        elif stream_callback and event_type in ["response", "stream", "message"]:
                            text = data.get("response") or data.get("stream") or data.get("message")
                            if text:
                                stream_callback(text)

                        elif stream_callback and event_type == "tool":
                            tool_data = data.get("tool")
                            if tool_data:
                                stream_callback(f"[TOOL] {json.dumps(tool_data)}")

                    except websockets.exceptions.ConnectionClosed:
                        logger.error("WebSocket connection closed unexpectedly")
                        self.connected = False
                        raise

            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                retry_count += 1
                last_error = e
                
                # Close connection on error
                await self.disconnect()
                
                if retry_count >= max_retries:
                    raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
                
                # Wait before retrying
                await asyncio.sleep(1)

        raise Exception(f"Failed after {max_retries} attempts: {str(last_error)}")

    async def upload_file(self, file_path: str) -> dict:
        """Uploads a file to the worker via HTTP.
        
        Args:
            file_path (str): Path to the file to upload
            
        Returns:
            dict: Response from the worker containing upload status
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'files': (file_path.split('/')[-1], f)}
                response = requests.post(f"{self.http_url}/upload", files=files)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise
