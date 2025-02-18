from typing import Optional
from autoppia_sdk.src.integrations.implementations.api.interface import APIIntegration
from autoppia_sdk.src.integrations.config import IntegrationConfig
from autoppia_sdk.src.integrations.implementations.base import Integration
import requests


class GoogleIntegration(Integration):
    """Integration class for performing web searches using Google Custom Search API.

    This class provides functionality to search the web using Google's Custom Search API.
    It requires valid Google API credentials (API key and Search Engine ID) to function.

    Attributes:
        integration_config (IntegrationConfig): Configuration object containing integration settings
        google_api_key (str): Google API key for authentication
        google_search_engine_id (str): Google Custom Search Engine ID
    """
    
    def __init__(self, integration_config: IntegrationConfig):
        
        self.integration_config = integration_config
        self.google_api_key = integration_config.attributes.get("google_api_key")
        self.google_search_engine_id = integration_config.attributes.get("google_search_engine_id")

    def call_endpoint(
        self,
        query: str,
        num_results: int = 5
    ):
        """Performs a web search using Google Custom Search API.

        Args:
            query (str): The search query string
            num_results (int, optional): Number of search results to return. Defaults to 5.

        Returns:
            list[dict]: A list of dictionaries containing search results, each with:
                - title: The title of the search result
                - link: The URL of the search result
                - snippet: A brief excerpt from the search result

        Note:
            Returns an empty list if the API request fails or if there's an error parsing the response.
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_search_engine_id,
                "q": query,
                "num": num_results,
            }
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            results = response.json().get("items", [])
            return [
                {"title": item["title"], "link": item["link"], "snippet": item["snippet"]}
                for item in results
            ]
        except requests.RequestException as e:
            print(f"Error making request: {str(e)}")
            return []
        
        except (KeyError, ValueError) as e:
            print(f"Error parsing response: {str(e)}")
            return []

    