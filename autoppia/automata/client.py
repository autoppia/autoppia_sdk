import httpx
import asyncio
import logging
from typing import Any, Dict, Optional, List, Literal

logger = logging.getLogger(__name__)

class AutomataClient:
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url or "https://api-automata.autoppia.com/api/v1"
        self.timeout = timeout
        self.max_retries = max_retries

        self.headers = {
            "User-Agent": "Autoppia SDK",
        }

        if self.api_key:
            self.headers["x-api-key"] = self.api_key
    
    async def run_task(
        self, 
        task: str, 
        initial_url: Optional[str] = None
    ) -> str:
        """
        Run a specified task by sending a request to the task endpoint.

        Args:
            task (str): The name of the task to run.
            initial_url (Optional[str]): An optional URL to include in the payload.

        Returns:
            Dict[str, str]: The JSON response from the server after executing the task.

        Raises:
            httpx.HTTPError: If the request to run the task fails.
        """        
        payload = {
            "task": task,
            "url": initial_url
        }

        endpoint = f"{self.base_url}/run-task"

        try:
            response = await self._execute_with_retry(endpoint, "POST", payload)
            return response["task_id"]
        except Exception as e:
            logger.error(f"Failed to run task: {e}")
            raise
    
    async def get_task(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve the details of a specific task by its ID.

        Args:
            task_id (str): The ID of the task to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the task details.

        Raises:
            httpx.HTTPError: If the request to get the task fails.
        """
        endpoint = f"{self.base_url}/task/{task_id}"

        try:
            response = await self._execute_with_retry(endpoint)
            return response
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            raise

    async def get_task_status(
        self,
        task_id: str
    ) -> str:
        """
        Retrieve the status of a specific task by its ID.

        Args:
            task_id (str): The ID of the task whose status is to be retrieved.

        Returns:
            Dict[str, Any]: A dictionary containing the task status.

        Raises:
            httpx.HTTPError: If the request to get the task status fails.
        """
        endpoint = f"{self.base_url}/task/{task_id}/status"

        try:
            response = await self._execute_with_retry(endpoint)
            return response["status"]
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise
    
    async def get_task_screenshots(
        self,
        task_id: str
    ) -> List[str]:
        """
        Retrieve the screenshots of a specific task by its ID.

        Args:
            task_id (str): The ID of the task whose screenshots are to be retrieved.

        Returns:
            Dict[str, Any]: A dictionary containing the task screenshots.

        Raises:
            httpx.HTTPError: If the request to get the task screenshots fails.
        """
        endpoint = f"{self.base_url}/task/{task_id}/screenshots"

        try:
            response = await self._execute_with_retry(endpoint)
            return response["screenshots"]
        except Exception as e:
            logger.error(f"Failed to get task screenshots: {e}")
            raise

    async def get_task_gif(
        self,
        task_id: str
    ) -> str:
        """
        Retrieve the GIF of a specific task by its ID.

        Args:
            task_id (str): The ID of the task whose GIF are to be retrieved.

        Returns:
            Dict[str, Any]: A dictionary containing the task GIF.

        Raises:
            httpx.HTTPError: If the request to get the task GIF fails.
        """
        endpoint = f"{self.base_url}/task/{task_id}/gif"

        try:
            response = await self._execute_with_retry(endpoint)
            return response["gif"]
        except Exception as e:
            logger.error(f"Failed to get task gif: {e}")
            raise

    async def start_cua(
        self, 
        task: str,
        provider: Literal["openai"] = "openai",
        display_width: int = 1024,
        display_height: int = 768
    ) -> Dict[str, Any]:
        payload = {
            "task": task,
            "provider": provider,
            "display_width": display_width,
            "display_height": display_height
        }

        endpoint = f"{self.base_url}/cua/start"

        try:
            response = await self._execute_with_retry(endpoint, "POST", payload)
            return response
        except Exception as e:
            logger.error(f"Failed to start CUA: {e}")
            raise

    async def forward_cua(
        self,
        agent_id: str,
        user_input: Optional[str] = None,
        screenshot: Optional[str] = None,
        current_url: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {            
            "user_input": user_input,
            "screenshot": screenshot,
            "current_url": current_url
        }

        endpoint = f"{self.base_url}/cua/{agent_id}/forward"

        try:
            response = await self._execute_with_retry(endpoint, "PUT", payload)
            return response
        except Exception as e:
            logger.error(f"Failed to forward CUA: {e}")
            raise

    async def stop_cua(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/cua/{agent_id}/stop"

        try:
            response = await self._execute_with_retry(endpoint, "PUT")
            return response
        except Exception as e:
            logger.error(f"Failed to stop CUA: {e}")
            raise

    async def get_cua_gif(
        self,
        agent_id: str
    ) -> str:
        endpoint = f"{self.base_url}/cua/{agent_id}/gif"

        try:
            response = await self._execute_with_retry(endpoint)
            return response
        except Exception as e:
            logger.error(f"Failed to get CUA gif: {e}")
            raise

    async def _execute_with_retry(
        self,
        endpoint: str,
        method: Optional[str] = "GET",
        payload: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an HTTP request with retry logic.

        Args:
            endpoint (str): The API endpoint to call.
            method (Optional[str]): The HTTP method to use (default is "GET").
            payload (Optional[Dict[str, str]]): The JSON payload to send with the request.

        Returns:
            Dict[str, str]: The JSON response from the server.

        Raises:
            httpx.HTTPError: If the request fails after the maximum number of retries.
        """
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method,
                        endpoint,
                        json=payload,
                        headers=self.headers,
                        timeout=self.timeout,
                    )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"HTTP error occurred: {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying... ({attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(1)
                    continue
                else:
                    logger.error(f"Max retries reached. Failed to execute request.")
                    raise 
