from typing import Optional
from autoppia_sdk.src.integrations.implementations.api.interface import APIIntegration
from autoppia_sdk.src.integrations.config import IntegrationConfig
from autoppia_sdk.src.integrations.implementations.base import Integration
import requests


class WebSearchIntegration(Integration):
    
    def __init__(self, integration_config: IntegrationConfig):
        
        self.integration_config = integration_config
        self.google_api_key = integration_config.attributes.get("google_api_key")
        self.google_search_engine_id = integration_config.attributes.get("google_search_engine_id")

    def call_endpoint(
        self,
        query: str,
        num_results: int = 5
    ):
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

    