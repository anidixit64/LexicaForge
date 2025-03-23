"""Wiktionary data ingestion module.

This module handles the ingestion of etymology and cognate data from Wiktionary.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Set

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from lexicaforge.core.logging import logger

class WiktionaryIngester:
    """Handles ingestion of data from Wiktionary."""

    def __init__(
        self,
        output_dir: Path,
        languages: Optional[List[str]] = None,
        batch_size: int = 100
    ):
        """Initialize the Wiktionary ingester.
        
        Args:
            output_dir: Directory to store ingested data
            languages: List of language codes to ingest (default: None for all)
            batch_size: Number of words to process in each batch
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.languages = languages or []
        self.batch_size = batch_size
        self.base_url = "https://en.wiktionary.org/w/api.php"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Set up the aiohttp session."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the aiohttp session."""
        if self.session:
            await self.session.close()

    async def _fetch_page_content(self, title: str) -> Optional[str]:
        """Fetch content of a Wiktionary page.
        
        Args:
            title: The page title to fetch
            
        Returns:
            Optional[str]: The page content if successful, None otherwise
        """
        if not self.session:
            raise RuntimeError("Session not initialized")

        params = {
            "action": "parse",
            "page": title,
            "format": "json",
            "prop": "text",
            "contentmodel": "wikitext"
        }

        try:
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "parse" in data:
                        return data["parse"]["text"]["*"]
                return None
        except Exception as e:
            logger.error(f"Error fetching page {title}: {e}")
            return None

    def _extract_etymology(self, content: str) -> Dict:
        """Extract etymology information from page content.
        
        Args:
            content: The page content to parse
            
        Returns:
            Dict: Extracted etymology information
        """
        soup = BeautifulSoup(content, "html.parser")
        etymology = {
            "origin": [],
            "cognates": [],
            "derived_terms": [],
            "related_terms": []
        }

        # Find etymology section
        etymology_section = soup.find(id="Etymology")
        if etymology_section:
            etymology_div = etymology_section.find_next("div", class_="mw-parser-output")
            if etymology_div:
                # Extract origin information
                for p in etymology_div.find_all("p"):
                    if "From" in p.text:
                        etymology["origin"].append(p.text.strip())

        # Find cognates section
        cognates_section = soup.find(id="Cognates")
        if cognates_section:
            cognates_list = cognates_section.find_next("ul")
            if cognates_list:
                etymology["cognates"] = [
                    li.text.strip() for li in cognates_list.find_all("li")
                ]

        return etymology

    async def _process_word(self, word: str) -> Optional[Dict]:
        """Process a single word from Wiktionary.
        
        Args:
            word: The word to process
            
        Returns:
            Optional[Dict]: Processed word data if successful, None otherwise
        """
        content = await self._fetch_page_content(word)
        if not content:
            return None

        etymology = self._extract_etymology(content)
        return {
            "word": word,
            "etymology": etymology,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def ingest_words(self, words: List[str]) -> List[Dict]:
        """Ingest a list of words from Wiktionary.
        
        Args:
            words: List of words to ingest
            
        Returns:
            List[Dict]: List of processed word data
        """
        results = []
        for i in tqdm(range(0, len(words), self.batch_size)):
            batch = words[i:i + self.batch_size]
            tasks = [self._process_word(word) for word in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend([r for r in batch_results if r is not None])
            
            # Save intermediate results
            if results:
                self._save_results(results)
        
        return results

    def _save_results(self, results: List[Dict]) -> None:
        """Save processed results to disk.
        
        Args:
            results: List of processed word data
        """
        df = pd.DataFrame(results)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"wiktionary_data_{timestamp}.parquet"
        df.to_parquet(output_file)
        logger.info(f"Saved {len(results)} results to {output_file}")

    async def get_word_list(self) -> List[str]:
        """Get list of words to process from Wiktionary.
        
        Returns:
            List[str]: List of words to process
        """
        if not self.session:
            raise RuntimeError("Session not initialized")

        words = set()
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:English lemmas",
            "cmlimit": "max",
            "format": "json"
        }

        while True:
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    break

                data = await response.json()
                if "query" not in data:
                    break

                for member in data["query"]["categorymembers"]:
                    words.add(member["title"])

                if "continue" not in data:
                    break

                params["cmcontinue"] = data["continue"]["cmcontinue"]

        return sorted(list(words)) 