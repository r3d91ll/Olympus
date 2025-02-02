"""
ArangoDB Documentation Scraper

This script fetches ArangoDB documentation from their GitHub repository
and saves it in markdown format.
"""

import os
import asyncio
import aiohttp
import base64
from typing import Dict, List, Set
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ArangoDocScraper:
    """Fetches ArangoDB documentation from GitHub."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.session: aiohttp.ClientSession = None
        self.api_base = "https://api.github.com"
        self.repo = "arangodb/docs"
        self.branch = "main"
        
    async def init_session(self):
        """Initialize aiohttp session with headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ArangoDocScraper"
        }
        self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    async def fetch_directory_content(self, path: str = "") -> List[Dict]:
        """Fetch directory contents from GitHub."""
        url = f"{self.api_base}/repos/{self.repo}/contents/{path}"
        if path:
            url += f"?ref={self.branch}"
            
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            logging.warning(f"Failed to fetch directory {path}, status: {response.status}")
            return []

    async def fetch_file_content(self, path: str) -> str:
        """Fetch file content from GitHub."""
        url = f"{self.api_base}/repos/{self.repo}/contents/{path}?ref={self.branch}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("encoding") == "base64":
                    return base64.b64decode(data["content"]).decode('utf-8')
            logging.warning(f"Failed to fetch file {path}, status: {response.status}")
            return None

    async def process_directory(self, path: str = ""):
        """Process a directory and its contents recursively."""
        contents = await self.fetch_directory_content(path)
        
        for item in contents:
            if item["type"] == "dir":
                await self.process_directory(item["path"])
            elif item["type"] == "file" and item["name"].endswith((".md", ".mdx")):
                content = await self.fetch_file_content(item["path"])
                if content:
                    # Create the directory structure
                    dir_path = os.path.join(self.output_dir, os.path.dirname(item["path"]))
                    os.makedirs(dir_path, exist_ok=True)
                    
                    # Save the file
                    file_path = os.path.join(self.output_dir, item["path"])
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"---\nsource: {item['html_url']}\n---\n\n{content}")
                    
                    logging.info(f"Saved {item['path']}")

    async def scrape(self):
        """Main scraping function."""
        await self.init_session()
        try:
            await self.process_directory()
        finally:
            await self.close_session()

def main():
    """Main entry point."""
    output_dir = "/home/todd/ML-Lab/Olympus/datasets/arangodb_docs"
    
    scraper = ArangoDocScraper(output_dir)
    asyncio.run(scraper.scrape())
    
    logging.info("Documentation scraping completed!")

if __name__ == "__main__":
    main()
