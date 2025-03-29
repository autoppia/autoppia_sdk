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
    
    def call(self, message: str, stream_callback=None, keep_alive=False):
        """Sends a message to the worker for processing via Socket.IO.
        
        Args:
            message (str): The message to send to the worker
            stream_callback (callable, optional): Callback function to handle streaming responses
                If provided, streaming messages will be passed to this function
            keep_alive (bool, optional): If True, the connection will be kept alive indefinitely
        
        Returns:
            The final result from the worker
        """
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                logger.info(f"Connecting to worker at {self.socketio_url} (attempt {retry_count+1}/{max_retries})")
                
                # Create a new Socket.IO client with improved reconnection settings
                sio = socketio.Client(reconnection=True, reconnection_attempts=5, 
                                     reconnection_delay=1, reconnection_delay_max=5,
                                     logger=logger, engineio_logger=False)
                final_result = None
                request_completed = False
                connection_established = False
                connection_error = None
                
                # Set up event handlers
                @sio.event
                def connect():
                    nonlocal connection_established
                    connection_established = True
                    logger.info("Connected to SocketIO server")
                    # Send the message after connection is established
                    sio.emit('message', {"message": message})
                    logger.info(f"Sent message: {message[:50]}...")
                
                @sio.event
                def connect_error(data):
                    nonlocal connection_error
                    connection_error = data
                    logger.error(f"Connection error: {data}")
                
                @sio.event
                def disconnect():
                    logger.info("Disconnected from SocketIO server")
                    # Only raise an exception if we haven't completed the request
                    if not request_completed:
                        logger.warning("Disconnected before request completion")
                
                @sio.on('response')
                def on_response(data):
                    logger.info(f"Received response: {data}")
                
                @sio.on('stream')
                def on_stream(data):
                    stream_content = data.get("stream", "")
                    logger.info(f"Received streaming content: {stream_content[:100]}...")
                    if stream_callback:
                        try:
                            # Handle both JSON and string formats
                            if isinstance(stream_content, str):
                                try:
                                    parsed_content = json.loads(stream_content)
                                    stream_callback(parsed_content)
                                except json.JSONDecodeError:
                                    stream_callback(stream_content)
                            else:
                                stream_callback(stream_content)
                        except Exception as e:
                            logger.error(f"Error in stream callback: {e}")
                
                @sio.on('message')
                def on_message(data):
                    logger.info(f"Received direct message: {data}")
                    if stream_callback:
                        try:
                            if isinstance(data, dict) and "text" in data:
                                stream_callback(data["text"])
                            else:
                                stream_callback(data)
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
                    # Don't disconnect immediately to ensure all messages are processed
                
                @sio.on('result')
                def on_result(data):
                    nonlocal final_result, request_completed
                    final_result = data.get("result")
                    request_completed = True
                    logger.info(f"Received result message: {data}")
                    # Don't disconnect immediately to ensure all messages are processed
                
                @sio.on('error')
                def on_error(data):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Worker returned an error: {error_msg}")
                    raise Exception(f"Worker error: {error_msg}")
                
                @sio.on('heartbeat')
                def on_heartbeat(data):
                    logger.debug("Received heartbeat")
                
                # Connect to the server with timeout
                connect_timeout = 10  # 10 seconds timeout for connection
                try:
                    sio.connect(self.socketio_url, wait_timeout=connect_timeout)
                except Exception as e:
                    logger.error(f"Failed to connect within {connect_timeout} seconds: {e}")
                    retry_count += 1
                    last_error = e
                    time.sleep(1)  # Wait before retrying
                    continue  # Skip the rest of the loop and try again
                
                # Wait for connection to be established
                connection_wait_time = 0
                while not connection_established and connection_wait_time < 5 and not connection_error:
                    time.sleep(0.5)
                    connection_wait_time += 0.5
                
                if not connection_established:
                    if connection_error:
                        raise Exception(f"Failed to establish connection: {connection_error}")
                    else:
                        raise Exception("Timed out waiting for connection to establish")
                
                # Wait for a response with timeout
                timeout = 300  # 5 minutes timeout
                start_time = time.time()
                
                while not request_completed and time.time() - start_time < timeout:
                    time.sleep(0.1)  # Small sleep to prevent CPU hogging
                
                if not request_completed:
                    logger.error("Request timed out")
                    sio.disconnect()
                    raise Exception("Request timed out waiting for response")
                
                if not keep_alive:            
                    # Add a small delay before disconnecting to ensure all messages are processed
                    time.sleep(1)
                    
                    # Gracefully disconnect
                    if sio.connected:
                        sio.disconnect()

                    return final_result
                
                else:
                    return final_result, sio
                
            except socketio.exceptions.ConnectionError as e:
                logger.warning(f"SocketIO connection error: {e}")
                retry_count += 1
                last_error = e
                if retry_count >= max_retries:
                    logger.error("Max retries reached for connection")
                    raise Exception(f"Failed to connect to SocketIO server: {str(e)}")
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                retry_count += 1
                last_error = e
                if retry_count >= max_retries:
                    raise Exception(f"Failed to call worker via SocketIO: {str(e)}")
                time.sleep(1)  # Wait before retrying
        
        # If we've exhausted all retries without returning, raise the last error
        if last_error:
            raise Exception(f"Failed to call worker after {max_retries} attempts: {str(last_error)}")
        else:
            raise Exception(f"Failed to call worker after {max_retries} attempts with unknown error")
