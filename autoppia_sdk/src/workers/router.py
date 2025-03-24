import json
import logging
import requests
import time
import socketio
from autoppia_sdk.src.workers.adapter import AIWorkerConfigAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerRouter")

class WorkerRouter():
    """A router class for handling communication with AI workers via Socket.IO.

    This class manages the routing and communication with AI worker instances,
    handling configuration retrieval and message processing.
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
        self.socketio_url = f"http://{self.ip}:{self.port}"
        logger.info(f"Initialized WorkerRouter with SocketIO URL: {self.socketio_url}")
    
    def call(self, message: str, stream_callback=None):
        """Sends a message to the worker for processing via Socket.IO.
        
        Args:
            message (str): The message to send to the worker
            stream_callback (callable, optional): Callback function to handle streaming responses
                If provided, streaming messages will be passed to this function
        
        Returns:
            The final result from the worker
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Connecting to worker at {self.socketio_url} (attempt {retry_count+1}/{max_retries})")
                
                # Create a new Socket.IO client
                sio = socketio.Client(reconnection=True, reconnection_attempts=3, 
                                     reconnection_delay=1, reconnection_delay_max=5)
                final_result = None
                request_completed = False
                
                # Set up event handlers
                @sio.event
                def connect():
                    logger.info("Connected to SocketIO server")
                    # Send the message after connection is established
                    sio.emit('message', {"message": message})
                    logger.info(f"Sent message: {message[:50]}...")
                
                @sio.event
                def connect_error(data):
                    logger.error(f"Connection error: {data}")
                
                @sio.event
                def disconnect():
                    logger.info("Disconnected from SocketIO server")
                
                @sio.on('response')
                def on_response(data):
                    logger.info(f"Received response: {data}")
                
                @sio.on('stream')
                def on_stream(data):
                    stream_content = data.get("stream", "")
                    logger.info(f"Received streaming content: {stream_content[:100]}...")
                    if stream_callback:
                        try:
                            stream_callback(json.loads(stream_content))
                        except Exception as e:
                            logger.error(f"Error in stream callback: {e}")
                
                @sio.on('message')
                def on_message(data):
                    logger.info(f"Received direct message: {data}")
                    if stream_callback and "text" in data:
                        try:
                            stream_callback(data["text"])
                        except Exception as e:
                            logger.error(f"Error in message callback: {e}")
                
                @sio.on('tool')
                def on_tool(data):
                    tool_info = data.get("tool", {})
                    logger.info(f"Received tool message: {tool_info}")
                    if stream_callback:
                        try:
                            stream_callback(f"[TOOL] {json.dumps(tool_info)}")
                        except Exception as e:
                            logger.error(f"Error in tool callback: {e}")
                
                @sio.on('complete')
                def on_complete(data):
                    nonlocal final_result, request_completed
                    final_result = data.get("result")
                    request_completed = True
                    logger.info(f"Received completion message: {data}")
                    sio.disconnect()
                
                @sio.on('result')
                def on_result(data):
                    nonlocal final_result, request_completed
                    final_result = data.get("result")
                    request_completed = True
                    logger.info(f"Received result message: {data}")
                    sio.disconnect()
                
                @sio.on('error')
                def on_error(data):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Worker returned an error: {error_msg}")
                    raise Exception(f"Worker error: {error_msg}")
                
                @sio.on('heartbeat')
                def on_heartbeat(data):
                    logger.debug("Received heartbeat")
                
                # Connect to the server and wait for completion
                sio.connect(self.socketio_url)
                
                # Wait for a response with timeout
                timeout = 300  # 5 minutes timeout
                start_time = time.time()
                
                while not request_completed and time.time() - start_time < timeout:
                    time.sleep(0.1)  # Small sleep to prevent CPU hogging
                
                if not request_completed:
                    logger.error("Request timed out")
                    sio.disconnect()
                    raise Exception("Request timed out waiting for response")
                
                # Return the final result
                return final_result
                
            except socketio.exceptions.ConnectionError as e:
                logger.warning(f"SocketIO connection error: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error("Max retries reached for connection")
                    raise Exception(f"Failed to connect to SocketIO server: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed to call worker via SocketIO: {str(e)}")
