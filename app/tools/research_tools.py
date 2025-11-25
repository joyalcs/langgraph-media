import json
from app.faiss_cache import FaissCache
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

faiss_cache = FaissCache()
tavily = TavilySearch(max_results=5)

@tool
def faiss_recall_tool(query: str) -> str:
    """Search for cached research results in the FAISS vector database.
    
    This tool performs a semantic similarity search against previously cached
    research queries and their results. If a similar query has been processed
    before, it returns the cached result instead of making a new API call,
    improving efficiency and reducing API costs.
    
    Args:
        query (str): The search query to look up in the cache. Should be a
            clear, descriptive research question or topic.
    
    Returns:
        str: The cached search results as a JSON string if found, or None if
            no similar cached query exists. Results include article titles,
            URLs, summaries, and other metadata from the original search.

    Note:
        - Uses semantic similarity, so exact query matches are not required
        - Returns the most similar cached result (k=1)
        - Cache grows over time as more searches are performed
        - Requires FAISS index to exist in the faiss_cache directory
    """
    return faiss_cache.search(query)

@tool
def tavily_search_tool(query: str) -> list:
    """Perform a fresh web search using Tavily API and cache the results.
    
    This tool executes a new web search query using the Tavily search API,
    retrieves up to 5 relevant results, and automatically saves the results
    to the FAISS vector database for future retrieval. Use this when cached
    results are not available or when you need the most current information.
    
    Args:
        query (str): The search query to execute. Should be a clear, specific
            question or topic. Supports natural language queries.
    
    Returns:
        list: A list of search result dictionaries. Each result typically contains:
            - title: Article/page title
            - url: Source URL
            - content: Snippet or summary of the content
            - score: Relevance score
            - published_date: Publication date (if available)
    Note:
        - Automatically caches results in FAISS for future retrieval
        - Returns up to 5 results (configured in tavily initialization)
        - Requires valid Tavily API key in environment variables
        - Results are saved as JSON string in the cache
        - Use faiss_recall_tool first to check cache before calling this
    """
    result = tavily.invoke({"query": query})
    faiss_cache.save(query, json.dumps(result))
    return result
