import json
import asyncio
from app.core.state import State
from app.agents.base_agent import llm_model
from app.tools.research_tools import faiss_recall_tool, tavily_search_tool
from app.tools.firecrawl_tool import parse_the_data
from langgraph.prebuilt import create_react_agent
from app.faiss_cache import FaissCache
faiss_cache = FaissCache()
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
    3. Focus on specific entities, topics, and keywords mentioned in the user intent.
    4. Remove instruction words like "Search for", "Find", "Extract", "Analyze".
    5. STAY TRUE to the user's original intent - DO NOT add topics not mentioned.
    6. Use the exact entities, names, or keywords from the user intent.
    """
    
    user_prompt = f"""
    ### User's Original Intent:
    {intent}
    
    ### Scope of Research:
    {section.get('scope_of_research')}
    
    ### Section Title:
    {section.get('title')}
    
    IMPORTANT: Base your query primarily on the User's Original Intent above.
    Only use Scope/Title to add context, NOT to change the topic.
    
    Generate the best search query:
    """
    
    try:
        response = await llm_model.ainvoke(system_prompt + "\n\n" + user_prompt)
        query = response.content.strip()
        
        # Remove quotes if present
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]
        
        # Remove common prefix patterns
        prefixes_to_remove = ["search for ", "find ", "query: ", "search: "]
        query_lower = query.lower()
        for prefix in prefixes_to_remove:
            if query_lower.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        
        # Hard truncation safety net
        if len(query) > 300:
            query = query[:300]
        
        # Fallback validation: ensure query relates to intent
        if not query or len(query) < 3:
            # Create simple fallback from intent
            query = intent.strip()[:200]
            
        return query
    except Exception as e:
        print(f"  -> Query Generation Error: {e}")
        # Fallback to user intent directly
        return intent.strip()[:200] if intent else section.get('title', '')[:200]


async def process_section(section, intent, agent):
    """
    Process a single section: generate query, run agent (search), and parse results.
    """
    query = await generate_search_query(section, intent)

    print("\n=== Running Agent for Query ===")
    print("QUERY:", query)
    
    try:
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )
    except Exception as e:
        print(f"Agent invocation error: {e}")
        return []

    section_results = []

    for msg in response["messages"]:
        if msg.__class__.__name__ == "ToolMessage":
            tool_name = msg.name        
            try:
                content = msg.content
                
                if content is None or content == "null":
                    continue
                
                data = json.loads(content)
                
                if tool_name == "faiss_recall_tool":
                    results = data.get("results", [])
                    print(f"FAISS returned {len(results)} results")
                    
                    for i, result in enumerate(results):
                        # Fixed: properly access result data
                        section_results.append({
                            "title": result.get("title", ""),
                            "description": result.get("content", result.get("description", "")),
                            "url": result.get("url", ""),
                        })
                    
                    print(f"FAISS results processed: {len(section_results)}")
                    
                elif tool_name == "tavily_search_tool":
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
                    
                    print(f"Tavily returned {len(results)} results")
                    
                    # Prepare tasks for parallel scraping
                    scrape_tasks = []
                    for item in results:
                        url = item.get("url")
                        if not url:
                            print("Skipping item without URL")
                            continue
                        scrape_tasks.append(parse_the_data(url))
                    
                    # Run scraping in parallel
                    if scrape_tasks:
                        print(f"Scraping {len(scrape_tasks)} URLs in parallel...")
                        scraped_data_list = await asyncio.gather(*scrape_tasks, return_exceptions=True)
                        
                        for i, parsed_data in enumerate(scraped_data_list):
                            if isinstance(parsed_data, Exception):
                                print(f"Error parsing URL {results[i].get('url', 'unknown')}: {parsed_data}")
                                continue
                            
                            if parsed_data and isinstance(parsed_data, dict):
                                print(f"Successfully parsed: {parsed_data.get('title', 'No title')}")
                                section_results.append({
                                    "title": parsed_data.get("title", results[i].get("title", "")),
                                    "description": parsed_data.get("description", parsed_data.get("content", "")),
                                    "url": parsed_data.get("url", results[i].get("url", "")),
                                })
                            else:
                                # Fallback: use original Tavily result
                                section_results.append({
                                    "title": results[i].get("title", ""),
                                    "description": results[i].get("content", results[i].get("description", "")),
                                    "url": results[i].get("url", ""),
                                })
                    faiss_cache.save(query, section_results)
            except json.JSONDecodeError as e:
                print(f"JSON decode error for {tool_name} result: {e}")
                print(f"Content was: {content[:200]}...")
                continue
            except Exception as e:
                print(f"Unexpected error processing {tool_name} result: {e}")
                import traceback
                traceback.print_exc()
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
    print(f"User Intent: {intent}")
    print(f"Total Sections: {len(sections)}")

    # ----------------------------
    # AGENT PROMPT
    # ----------------------------
    prompt = """
        You are an Autonomous Research Agent.

        Follow the EXACT WORKFLOW BELOW — DO NOT CHANGE IT:

        ──────────────────────────────────────────
        STEP 1 — FAISS RECALL  
        - Use faiss_recall_tool first with the user's query.
        - If FAISS returns NON-EMPTY results (len > 0):  
            • Stop immediately and return those results.
            • DO NOT perform Tavily search.
            • DO NOT call parse_the_data (FAISS data is already structured).
        ──────────────────────────────────────────
        STEP 2 — TAVILY SEARCH (only if FAISS was empty)  
        - Use tavily_search_tool with the same query.
        - Tavily returns a list of URLs and snippets.
        ──────────────────────────────────────────
        STEP 3 — RETURN RESULTS
        - Return the results from whichever tool provided data.
        - The parsing will be handled automatically after this.
        ──────────────────────────────────────────

        ⚡ IMPORTANT: 

        1. ALWAYS try FAISS first
        2. If FAISS has results, STOP - don't use Tavily
        3. Only use Tavily if FAISS returned empty
        4. Don't explain your actions, just execute the tools
        5. The user's query contains their true intent - respect it exactly
    """
    
    agent = create_react_agent(
        model=llm_model,
        tools=[faiss_recall_tool, tavily_search_tool],
        prompt=prompt
    )

    # Run sections in parallel
    print(f"\nProcessing {len(sections)} sections in parallel...")
    tasks = [process_section(section, intent, agent) for section in sections]
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Flatten results and handle exceptions
    research_results = []
    for i, result in enumerate(results_list):
        if isinstance(result, Exception):
            print(f"Error processing section {i}: {result}")
            continue
        if isinstance(result, list):
            research_results.extend(result)
        else:
            print(f"Unexpected result type from section {i}: {type(result)}")

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