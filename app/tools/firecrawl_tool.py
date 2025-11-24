from firecrawl import Firecrawl
import time
from langchain_groq import ChatGroq

firecrawl = Firecrawl(api_key="fc-012536fdba0a40cb9f31d7412c7afd7b")
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def parse_the_data(url):
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
