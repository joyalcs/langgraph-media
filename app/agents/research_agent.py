import json
import asyncio
from app.core.state import State
from app.agents.base_agent import llm_model
from app.tools.research_tools import faiss_recall_tool, tavily_search_tool
from app.tools.firecrawl_tool import parse_the_data_async
from langgraph.prebuilt import create_react_agent


async def generate_search_query(section, intent):
    """
    Generates a concise, keyword-optimized search query based on the section scope and user intent.
    """
    system_prompt = """
    You are a Search Query Optimizer.
    Your task is to convert a research scope into a single, concise, keyword-rich search query.
    
    RULES:
    1. Output ONLY the search query string. No quotes, no explanations.
    2. Keep it under 200 characters.
    3. Focus on specific entities, topics, and keywords.
    4. Remove instruction words like "Search for", "Find", "Extract", "Analyze".
    """
    
    user_prompt = f"""
    ### Scope of Research:
    {section.get('scope_of_research')}
    
    ### Section Title:
    {section.get('title')}
    
    ### User Intent:
    {intent}
    
    Generate the best search query:
    """
    
    try:
        response = await llm_model.ainvoke(system_prompt + "\n\n" + user_prompt)
        query = response.content.strip()
        
        # Remove quotes if present
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]
            
        # Hard truncation safety net
        if len(query) > 300:
            query = query[:300]
            
        return query
    except Exception as e:
        print(f"  -> Query Generation Error: {e}")
        # Fallback
        return f"{section.get('title')} {intent}"[:200]


async def process_section(section, intent, agent):
    """
    Process a single section: generate query, run agent (search), and parse results.
    """
    query = await generate_search_query(section, intent)

    print("\n=== Running Agent for Query ===")
    print("QUERY:", query)
    
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )

    section_results = []

    for msg in response["messages"]:
        if msg.__class__.__name__ == "ToolMessage":
            tool_name = msg.name        
            try:
                content = msg.content
                
                if content is None or content == "null":
                    continue
                
                data = json.loads(content)
                
                if data is None:
                    continue
                
                # Get results - handle both list and dict formats
                if isinstance(data, list):
                    results = data
                elif isinstance(data, dict):
                    results = data.get("results", [])
                else:
                    print(f"Unexpected Tavily data type: {type(data)}")
                    continue
                
                
                # Prepare tasks for parallel scraping
                scrape_tasks = []
                for item in results:
                    url = item.get("url")
                    if not url:
                        print("Skipping item without URL")
                        continue
                    scrape_tasks.append(parse_the_data_async(url))
                
                # Run scraping in parallel
                if scrape_tasks:
                    print(f"Scraping {len(scrape_tasks)} URLs in parallel...")
                    scraped_data_list = await asyncio.gather(*scrape_tasks, return_exceptions=True)
                    
                    for i, parsed_data in enumerate(scraped_data_list):
                        if isinstance(parsed_data, Exception):
                            print(f"Error parsing URL: {parsed_data}")
                            continue
                        
                        if parsed_data:
                            print("parsed data", parsed_data)
                            section_results.append({
                                "title": parsed_data.get("title", ""),
                                "description": parsed_data.get("description", ""),
                                "url": parsed_data.get("url", results[i].get("url")), # Fallback to original URL
                            })

            except json.JSONDecodeError as e:
                print(f"JSON decode error for Tavily result: {e}")
                print(f"Content was: {content}")
                continue
            except Exception as e:
                print(f"Unexpected error processing Tavily result: {e}")
                continue
                
    return section_results


async def research_agent(state: State):
    """
    Research workflow:
        1. Try FAISS recall.
        2. If FAISS has results → RETURN DIRECTLY (NO PARSE, NO TAVILY).
        3. If empty → run Tavily search.
        4. Parse all Tavily URLs using parse_the_data.
        5. Return structured research data for writer agent.
    """

    sections = state.get("sections", [])
    intent = state.get("intent", "")

    print("=== RESEARCH AGENT INPUT ===")
    print(f"Total Sections: {len(sections)}")

    # ----------------------------
    # AGENT PROMPT
    # ----------------------------
    prompt = """
        You are an Autonomous Research Agent.

        Follow the EXACT WORKFLOW BELOW — DO NOT CHANGE IT:

        ──────────────────────────────────────────
        STEP 1 — FAISS RECALL  
        - Use faiss_recall_tool first.  
        - If FAISS returns NON-EMPTY results (len > 0):  
            • Immediately return:  
                [{"url": "<faiss_url>"}]  
            • DO NOT perform Tavily search.  
        ──────────────────────────────────────────
        STEP 2 — TAVILY SEARCH (only if FAISS was empty)  
        - Use tavily_search_tool.  
        - Tavily returns a list of URLs.
        ──────────────────────────────────────────
        STEP 3 — PARSE (required for Tavily results)  
        - For EVERY URL returned by Tavily:  
            • Call parse_the_data  
        ──────────────────────────────────────────

        ⚡ IMPORTANT: OUTPUT RULES (READ CAREFULLY)

        You MUST:
        1. Understand the user's intent from the query.
        2. Infer what type of data they expect (movies, matches, gadgets, news, research facts).
        3. Use ONLY the parsed data from the tools.
        4. NEVER hallucinate anything not found.

        Your FINAL OUTPUT MUST:
        - Always be **valid JSON**.
        - Always be a **list**.
        - Automatically adapt structure based on the query.

        EXAMPLES OF AUTO-ADAPTED OUTPUT:
        - If the query is about movies → each item contains movie fields (title, release_date, url, etc.)
        - If the query is about sports → include match fields (teams, score, date, url, etc.)
        - If the query is about tech → include product fields (name, specs, launch_date, url, etc.)
        - If the query is general research → return articles (title, summary, publication_date, url)
        - If unsure → return the best structured representation based on parsed data.

        DO NOT use a fixed schema.
        DO NOT return explanations.
        DO NOT wrap output in code blocks.

        Your output must ALWAYS be a JSON list of objects based on the query’s intention.
    """
    
    agent = create_react_agent(
        model=llm_model,
        tools=[faiss_recall_tool, tavily_search_tool],
        prompt=prompt
    )

    # Run sections in parallel
    tasks = [process_section(section, intent, agent) for section in sections]
    results_list = await asyncio.gather(*tasks)
    
    # Flatten results
    research_results = [item for sublist in results_list for item in sublist]

    print(f"\n=== RESEARCH COMPLETE ===")
    print(f"Total results collected: {len(research_results)}")
    
    state["research_data"] = research_results
    return state


def extract_data_with_llm(search_results, section, intent):
    """
    Helper function to extract structured data from raw search results using LLM.
    """
    
    system_prompt = """
    You are a Research Extraction Agent.
    Your task is to extract factual information from the provided search results.
    
    EXTRACT:
    - URLs
    
    RULES:
    1. Use ONLY the provided search results. Do NOT hallucinate.
    2. If a result is irrelevant to the section topic, ignore it.
    3. Return valid JSON only.
    """
    
    user_prompt = f"""
    ### Section Goal:
    {section.get('title')}
    {section.get('scope_of_research')}
    
    ### User Intent:
    {intent}
    
    ### Raw Search Results:
    {json.dumps(search_results, indent=2, default=str)}
    
    ### Output JSON Schema:
    {{
        "articles": [
            {{
                "headline": "string",
                "summary": "string",
                "publication_date": "string",
                "source": "string",
                "url": "string",
                "quotes": ["string"]
            }}
        ]
    }}
    """
    
    try:
        response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
        content = response.content.strip()
        
        # Clean up code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "", 1)
        if content.startswith("```"):
            content = content.replace("```", "", 1)
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
            
        return json.loads(content.strip())
        
    except Exception as e:
        print(f"  -> Extraction Error: {e}")
        return {"articles": []}