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
    
    print("====================PERFORMING faiss_recall_tool===============================")
    
    # Check if query exists with good score
    has_good_match = faiss_cache.search_with_score(query)
    print("Has good match:", has_good_match)
    
    # Get the actual result
    result = faiss_cache.search(query)
    print("Result:", result)
    
    return result

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
    
    try:
        # Check cache first
        print("====================PERFORMING tavily_search_tool===============================")
        
        cached_result = faiss_cache.search(query, threshold=0.7)
        if cached_result:
            print("✅ Cache hit - returning cached result")
            return cached_result
        
        print("❌ Cache miss - performing new search")
        
        # Initialize Tavily search
        search = TavilySearch(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            include_images=False,
        )
        
        # Perform search
        result = search.invoke({"query": query})
        
        # ✅ Validate result is serializable
        if not isinstance(result, (dict, list, str)):
            result = {"results": str(result)}
        
        # Convert to JSON string
        result_json = json.dumps(result, ensure_ascii=False, indent=2)
        
        # Save to cache
        faiss_cache.save(query, result_json)
        print(f"✅ Search successful - cached result ({len(result_json)} chars)")
        
        return result_json
        
    except ConnectionError as e:
        # ✅ Handle connection errors specifically
        error_msg = {
            "error": "ConnectionError",
            "message": "Failed to connect to Tavily API. Please check network connection and API configuration.",
            "details": str(e),
            "query": query
        }
        print(f"❌ Connection Error: {error_msg['message']}")
        return json.dumps(error_msg)
        
    except Exception as e:
        # ✅ Handle all other errors
        error_msg = {
            "error": type(e).__name__,
            "message": str(e),
            "query": query
        }
        print(f"❌ Error in tavily_search_tool: {type(e).__name__}: {str(e)}")
        
        # Don't cache errors
        return json.dumps(error_msg)
    
    

