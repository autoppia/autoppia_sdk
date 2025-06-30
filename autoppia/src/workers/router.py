import json
import logging
import requests
import time
import sseclient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerRouter")

class WorkerRouter():
    """A router class for handling communication with AI workers via HTTP.

    This class manages the routing and communication with AI worker instances,
    handling configuration retrieval and message processing through HTTP/SSE.
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
        self.base_url = f"http://{self.ip}:{self.port}"
        logger.info(f"Initialized WorkerRouter with base URL: {self.base_url}")

    def call(self, message: str, stream_callback=None):
        """Sends a message to the worker for processing.
        
        Args:
            message (str): The message to send to the worker
            stream_callback (callable, optional): Callback function to handle streaming responses
                If provided, streaming messages will be passed to this function
        
        Returns:
            The final result from the worker
        """
        max_retries = 3
        retry_count = 0
        last_error = None
        endpoint = f"{self.base_url}/call"
        
        while retry_count < max_retries:
            try:
                # Prepare request data
                data = {"message": message}
                headers = {"Content-Type": "application/json"}
                
                if stream_callback:
                    # Streaming request
                    data["stream"] = True
                    headers["Accept"] = "text/event-stream"
                    
                    response = requests.post(endpoint, json=data, headers=headers, stream=True)
                    response.raise_for_status()
                    
                    client = sseclient.SSEClient(response)
                    final_result = None
                    
                    for event in client.events():
                        try:
                            data = json.loads(event.data)
                            event_type = data.get("type")
                            
                            if event_type == "error":
                                error_msg = data.get("error", "Unknown error")
                                raise Exception(f"Worker error: {error_msg}")
                            
                            elif event_type == "complete":
                                final_result = data.get("result")
                                break
                            
                            elif stream_callback:
                                if event_type == "stream":
                                    stream_callback(data.get("stream"))
                                elif event_type == "message":
                                    stream_callback(data.get("message"))
                                elif event_type == "tool":
                                    stream_callback(f"[TOOL] {json.dumps(data.get('tool'))}")
                                elif event_type == "response":
                                    stream_callback(data.get("response"))
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse SSE data: {e}")
                            continue
                    
                    return final_result
                    
                else:
                    # Non-streaming request
                    response = requests.post(endpoint, json=data, headers=headers)
                    response.raise_for_status()
                    
                    result = response.json()
                    if not result.get("success"):
                        raise Exception(result.get("error", "Unknown error"))
                    
                    return result.get("result")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"HTTP request error: {e}")
                retry_count += 1
                last_error = e
                if retry_count >= max_retries:
                    logger.error("Max retries reached for HTTP request")
                    raise Exception(f"Failed to connect to HTTP server: {str(e)}")
                time.sleep(1)  # Wait before retrying
                
            except Exception as e:
                logger.error(f"Unexpected error in HTTP call: {str(e)}")
                retry_count += 1
                last_error = e
                if retry_count >= max_retries:
                    raise Exception(f"Failed to call worker: {str(e)}")
                time.sleep(1)  # Wait before retrying
        
        # If we've exhausted all retries without returning, raise the last error
        if last_error:
            raise Exception(f"Failed to call worker after {max_retries} attempts: {str(last_error)}")
        else:
            raise Exception(f"Failed to call worker after {max_retries} attempts with unknown error")
