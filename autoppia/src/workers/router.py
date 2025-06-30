import json
import logging
import requests
import time

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
                    
                    try:
                        logger.info(f"Initiating streaming request to {endpoint}")
                        response = requests.post(endpoint, json=data, headers=headers, stream=True)
                        logger.info(f"Streaming response received with status code: {response.status_code}")
                        logger.info(f"Response headers: {dict(response.headers)}")
                        response.raise_for_status()

                        final_result = None
                        current_data = ""
                        buffer = []

                        # Process the response line by line
                        for line in response.iter_lines(decode_unicode=True):
                            if line:
                                if line.startswith('data: '):
                                    buffer.append(line[6:])  # Remove 'data: ' prefix
                            else:
                                # Empty line indicates end of event
                                if buffer:
                                    try:
                                        # Join multi-line data if present
                                        json_str = ''.join(buffer).strip()
                                        if json_str:  # Only try to parse if we have data
                                            logger.debug(f"Parsing JSON: {json_str}")
                                            json_data = json.loads(json_str)
                                            
                                            event_type = json_data.get("type")
                                            if event_type == "error":
                                                error_msg = json_data.get("error", "Unknown error")
                                                logger.error(f"Worker returned error: {error_msg}")
                                                raise Exception(f"Worker error: {error_msg}")
                                            
                                            elif event_type == "complete":
                                                final_result = json_data.get("result", json_data.get("complete", None))
                                                logger.info("Received complete event")
                                                break
                                            
                                            elif event_type in ["response", "stream", "message"] and stream_callback:
                                                text = json_data.get("response") or json_data.get("stream") or json_data.get("message")
                                                if text:
                                                    stream_callback(text)
                                            
                                            elif event_type == "tool" and stream_callback:
                                                tool_data = json_data.get("tool")
                                                if tool_data:
                                                    stream_callback(f"[TOOL] {json.dumps(tool_data)}")
                                    except json.JSONDecodeError as e:
                                        logger.error(f"JSON parse error: {str(e)}")
                                        logger.error(f"Raw data: {buffer}")
                                    except Exception as e:
                                        logger.error(f"Error processing event: {str(e)}")
                                        logger.error(f"Raw data: {buffer}")
                                    finally:
                                        buffer = []  # Clear buffer after processing

                        if final_result is None:
                            final_result = "Message processed successfully"

                        return final_result

                    except Exception as e:
                        logger.error(f"Error in streaming request: {str(e)}")
                        raise

                    finally:
                        response.close()

                else:
                    # Non-streaming request
                    response = requests.post(endpoint, json=data, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    
                    if not result.get("success", True):
                        raise Exception(result.get("error", "Unknown error"))
                    
                    return result.get("result", result)

            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                retry_count += 1
                last_error = e
                if retry_count >= max_retries:
                    raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
                time.sleep(1)  # Wait before retrying

        raise Exception(f"Failed after {max_retries} attempts: {str(last_error)}")
