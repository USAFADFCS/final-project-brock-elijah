from tools.tool import Tool
from util.logs import Log
from keys.wallet import Key_Wallet
import re
from urllib.parse import unquote, urlparse, parse_qs
import requests
from typing import List, Dict
import json
from util.single_string_cleaner import clean_single_string


class GoogleSearchTool(Tool):
    name = "google-search-tool"
    description = """
    Accepts a single string argument, which is the phrase to search. Performs an internet search
    using the Google Custom Search JSON API to find relevant web sources for that phrase.
    Returns a JSON-compatible list of result dicts with `title`, `snippet`, and `link` fields.
    Be advised that search terms cannot be too complex, otherwise they will not have any results on 
    Google.
    """
    alias = "Search Google"

    def __init__(self, logger: Log, wallet: Key_Wallet):
        self.found_links: List[Dict] = []
        self.logger = logger
        # API key (required by keys.wallet)
        self.gs_api_key = wallet.get("GOOGLE_SEARCH")

        # Try to find a CX (search engine id) in the wallet first, otherwise from environment
        self.gs_cx = wallet.get("GOOGLE_CX")
        
        
    def _sanitize_url(self, url: str) -> str:
        # Remove common tracking params and unquote
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            # Remove typical tracking params
            for p in ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"]:
                qs.pop(p, None)
            # Rebuild query
            query = "&".join([f"{k}={v[0]}" for k, v in qs.items()]) if qs else ""
            cleaned = parsed._replace(query=query).geturl()
            return unquote(cleaned)
        except Exception:
            return url

    def _format_item(self, item: Dict) -> Dict:
        # Normalize fields coming from the Google API to a simpler dict
        return {
            "title": item.get("title"),
            "snippet": item.get("snippet") or item.get("htmlSnippet"),
            "link": self._sanitize_url(item.get("link") or item.get("formattedUrl") or ""),
            "displayLink": item.get("displayLink"),
        }

    def use(self, args: str, num: int = 15, start: int = 1, safe: str = "off") -> List[Dict]:
        args = clean_single_string(args)

        """
        Perform a search for `args` and return a list of result dicts.

        Parameters:
        - args: the search query string
        - num: number of results to return (max 10 per Google API limits)
        - start: the index of the first result (1-based)
        - safe: safeSearch setting: 'off'|'active'|'medium'

        Returns a list of dictionaries suitable for JSON serialization.
        """
        self.logger.log(f"[GOOGLE SEARCH TOOL] : searching for \"{args}\" (num={num}, start={start})")

        if not self.gs_api_key:
            self.logger.log("[GOOGLE SEARCH TOOL] : ERROR - missing GOOGLE_SEARCH API key")
            return False

        if not self.gs_cx:
            self.logger.log("[GOOGLE SEARCH TOOL] : ERROR - missing search engine id (GOOGLE_CX). Cannot perform search.")
            return False

        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.gs_api_key,
            "cx": self.gs_cx,
            "q": args,
            "num": max(1, min(10, int(num))),
            "start": max(1, int(start)),
            "safe": safe,
        }

        try:
            resp = requests.get(endpoint, params=params, timeout=10)
        except requests.RequestException as e:
            self.logger.log(f"[GOOGLE SEARCH TOOL] : Network error during search: {e}")
            return False

        if resp.status_code != 200:
            # Try to extract error details from the API response
            try:
                err = resp.json()
            except Exception:
                err = {"status_code": resp.status_code, "text": resp.text}
            self.logger.log(f"[GOOGLE SEARCH TOOL] : API error: {err}")
            return False

        data = resp.json()
        items = data.get("items", [])
        results: List[Dict] = []
        for it in items:
            formatted = self._format_item(it)
            results.append(formatted)

        self.found_links = results
        return json.dumps(results)

    



