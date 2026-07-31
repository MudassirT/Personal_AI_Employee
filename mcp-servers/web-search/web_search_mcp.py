#!/usr/bin/env python3
"""
Web Search MCP Server

Provides web search capabilities via multiple search engines.
Supports Google, Bing, DuckDuckGo, and custom search APIs.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)


class WebSearchClient:
    """Multi-engine web search client."""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        
        # API configurations
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.bing_api_key = os.getenv("BING_API_KEY")
        self.duckduckgo_html = "https://html.duckduckgo.com/html/"
    
    async def search_google(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using Google Custom Search API."""
        if not self.google_api_key or not self.google_cse_id:
            return [{"error": "Google API not configured"}]
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": min(num_results, 10)
        }
        
        response = await self.session.get(url, params=params)
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet"),
                "source": "google"
            })
        return results
    
    async def search_bing(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using Bing Web Search API."""
        if not self.bing_api_key:
            return [{"error": "Bing API not configured"}]
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "count": min(num_results, 50)}
        
        response = await self.session.get(url, headers=headers, params=params)
        data = response.json()
        
        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append({
                "title": item.get("name"),
                "url": item.get("url"),
                "snippet": item.get("snippet"),
                "source": "bing"
            })
        return results
    
    async def search_duckduckgo(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using DuckDuckGo HTML (no API key needed)."""
        params = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = await self.session.get(self.duckduckgo_html, params=params, headers=headers)
        
        # Simple HTML parsing for results
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:num_results]:
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')
            
            if title_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "url": url_elem.get_text(strip=True) if url_elem else "",
                    "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                    "source": "duckduckgo"
                })
        return results
    
    async def search_all(self, query: str, num_results: int = 10, 
                         engines: List[str] = None) -> Dict[str, List[Dict]]:
        """Search across multiple engines."""
        engines = engines or ["duckduckgo", "google", "bing"]
        results = {}
        
        tasks = []
        for engine in engines:
            if engine == "google":
                tasks.append(("google", self.search_google(query, num_results)))
            elif engine == "bing":
                tasks.append(("bing", self.search_bing(query, num_results)))
            elif engine == "duckduckgo":
                tasks.append(("duckduckgo", self.search_duckduckgo(query, num_results)))
        
        for engine, coro in tasks:
            try:
                results[engine] = await coro
            except Exception as e:
                results[engine] = [{"error": str(e)}]
        
        return results
    
    async def fetch_page(self, url: str) -> Dict:
        """Fetch and extract content from a webpage."""
        try:
            response = await self.session.get(url, follow_redirects=True)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            
            return {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "content": text[:5000],  # Limit content
                "status": response.status_code
            }
        except Exception as e:
            return {"url": url, "error": str(e)}
    
    async def close(self):
        await self.session.aclose()


# Global client
search_client: Optional[WebSearchClient] = None


async def get_search_client() -> WebSearchClient:
    global search_client
    if search_client is None:
        search_client = WebSearchClient()
    return search_client


server = Server("web-search")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(tools=[
        Tool(
            name="web_search",
            description="Search the web using multiple search engines",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "default": 10, "maximum": 50},
                    "engines": {"type": "array", "items": {"type": "string"}, 
                               "default": ["duckduckgo", "google", "bing"]}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="web_fetch",
            description="Fetch and extract content from a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="web_search_news",
            description="Search for recent news articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "News search query"},
                    "num_results": {"type": "integer", "default": 10},
                    "recency_days": {"type": "integer", "default": 7}
                },
                "required": ["query"]
            }
        ),
    ])


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        client = await get_search_client()
        
        if name == "web_search":
            results = await client.search_all(
                arguments["query"],
                arguments.get("num_results", 10),
                arguments.get("engines")
            )
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(results, indent=2))])
        
        elif name == "web_fetch":
            result = await client.fetch_page(arguments["url"])
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "web_search_news":
            # Add news-specific terms to query
            query = f"{arguments['query']} news"
            results = await client.search_all(query, arguments.get("num_results", 10))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(results, indent=2))])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
    
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())