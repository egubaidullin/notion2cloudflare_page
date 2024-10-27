import os
import requests
import logging
from typing import List, Dict, Any

class NotionClient:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"

    def get_page_content(self, page_id: str) -> List[Dict[str, Any]]:
        """Получает содержимое страницы Notion"""
        url = f"{self.base_url}/blocks/{page_id}/children"
        all_blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            try:
                params = {"page_size": 100}
                if start_cursor:
                    params["start_cursor"] = start_cursor

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                all_blocks.extend(data.get('results', []))
                has_more = data.get('has_more', False)
                start_cursor = data.get('next_cursor')

                logging.info(f"Fetched {len(data.get('results', []))} blocks. Total: {len(all_blocks)}")

            except requests.RequestException as e:
                logging.error(f"Error fetching Notion content: {e}")
                raise

        return all_blocks

    def get_page_title(self, page_id: str) -> str:
        """Получает заголовок страницы"""
        try:
            url = f"{self.base_url}/pages/{page_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            page_data = response.json()

            title_property = page_data.get("properties", {}).get("title", {}).get("title", [])
            if title_property:
                return title_property[0].get("text", {}).get("content", "Untitled")

            return "Untitled"

        except requests.RequestException as e:
            logging.error(f"Error fetching page title: {e}")
            return "Untitled"

    def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        """Получает дочерние блоки"""
        url = f"{self.base_url}/blocks/{block_id}/children"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            logging.error(f"Error fetching child blocks: {e}")
            return []