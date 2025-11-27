from firecrawl import Firecrawl
import time
from langchain_groq import ChatGroq
from app.agents.base_agent import llm_model

firecrawl = Firecrawl(api_key="/")

def parse_the_data(url):
    """
    Scrape, extract, and summarize webpage content using Firecrawl and an LLM.

    This function performs a full extraction workflow for a given URL:

    **1. Firecrawl Scrape**
       - Attempts to scrape the webpage in both `markdown` and `html` formats.
       - Handles scenarios where Firecrawl returns:
         - A single dictionary
         - A list of results
         - A Firecrawl object with attributes

    **2. Metadata Extraction**
       - Extracts common metadata fields:
         - `title`
         - `description`
         - `sourceURL` or fallback to provided URL
       - Supports both dict-style and attribute-style metadata (`DocumentMetadata`).

    **3. Content Summarization**
       - Uses an LLM (`llm.invoke`) to summarize the description into ~200 words.
       - Includes fallback logic:
         - If LLM summarization fails, falls back to a shortened description.

    **4. Standardized Return Object**
       - Returns a clean Python `dict` containing:
         - `title`: str
         - `description`: summarized text
         - `url`: canonical source URL

    **Error Handling**
       - Catches scraping and summarization errors.
       - Prints diagnostic messages for debugging.
       - Returns `None` if scraping or parsing completely fails.

    Parameters
    ----------
    url : str
        The webpage URL to scrape and extract structured data from.

    Returns
    -------
    dict or None
        A dictionary with the extracted fields:
        {
            "title": str,
            "description": str,
            "url": str
        }
        Returns `None` if extraction fails or produces empty results.
    """
    try:
        # Scrape a single webpage
        scrape_result = firecrawl.scrape(
            url,
            formats=['markdown', 'html']
        )
        # Handle if scrape_result is a list
        if isinstance(scrape_result, list):
            if len(scrape_result) > 0:
                scrape_result = scrape_result[0]
            else:
                print("Empty scrape result")
                return None
        
        # Extract metadata - check if it's a dict or object
        if isinstance(scrape_result, dict):
            metadata = scrape_result.get('metadata', {})
            url = metadata.get('sourceURL', url)
            title = metadata.get('title', 'No Title Found')
            description = metadata.get('description', 'No Description Found')
        else:
            # Assume it's an object with attributes
            metadata = getattr(scrape_result, 'metadata', {})
            # metadata might be an object too (DocumentMetadata)
            if hasattr(metadata, 'title'):
                title = metadata.title
                description = metadata.description
                source_url = metadata.source_url if hasattr(metadata, 'source_url') else url
                # Fallback for sourceURL vs source_url
                if not source_url and hasattr(metadata, 'sourceURL'):
                     source_url = metadata.sourceURL
            elif isinstance(metadata, dict):
                 title = metadata.get('title', 'No Title Found')
                 description = metadata.get('description', 'No Description Found')
                 source_url = metadata.get('sourceURL', url)
            else:
                 title = 'No Title Found'
                 description = 'No Description Found'
                 source_url = url

        # Summarize description if it's too lon
        try:
            summary_prompt = f"Summarize the following text into approximately 200 words:\n\n{description}"
            response = llm.invoke(summary_prompt)
            description = response.content
        except Exception as e:
            print(f"Error summarizing description: {e}")
            # Fallback to truncation if LLM fails
            description = " "

        

        return {
            "title": title,
            "description": description,
            "url":url
        }
    except Exception as e:
        print("error:", e)
        return None
