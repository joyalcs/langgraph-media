# # import json
# # from app.core.state import State
# # from app.agents.base_agent import llm_model
# # from langchain_core.prompts import ChatPromptTemplate
# from app.tools.firecrawl_tool import parse_the_data
# from langchain_groq import ChatGroq
# # from langchain_community.tools.tavily_search import TavilySearchResults
# # from langchain_tavily import TavilySearch

# llm_no_tools = ChatGroq(
#     model="openai/gpt-oss-20b",
#     temperature=0
# )

# # def research_agent(state: State = {}):
# #     sections = state.get('sections', [])
# #     print("========================research_agent INPUT========================", sections)
    
# #     intent = state.get('intent', '')
    
# #     # Define JSON schema for structured output
# #     json_schema = {
# #         "type": "object",
# #         "properties": {
# #             "sections": {
# #                 "type": "array",
# #                 "items": {
# #                     "type": "object",
# #                     "properties": {
# #                         "section_name": {"type": "string"},
# #                         "articles": {
# #                             "type": "array",
# #                             "items": {
# #                                 "type": "object",
# #                                 "properties": {
# #                                     "headline": {"type": "string"},
# #                                     "summary": {"type": "string"},
# #                                     "publication_date": {"type": "string"},
# #                                     "source": {"type": "string"},
# #                                     "url": {"type": "string"},
# #                                     "quotes": {"type": "array", "items": {"type": "string"}},
# #                                     "competitors_mentioned": {"type": "array", "items": {"type": "string"}},
# #                                     "entity_mentions": {"type": "array", "items": {"type": "string"}}
# #                                 },
# #                                 "required": ["headline", "summary", "publication_date", "source", "url"]
# #                             }
# #                         }
# #                     },
# #                     "required": ["section_name", "articles"]
# #                 }
# #             }
# #         },
# #         "required": ["sections"]
# #     }
    
# #     # Convert schema to string and escape curly braces for f-string
# #     schema_str = json.dumps(json_schema, indent=2).replace("{", "{{").replace("}", "}}")
    
# #     # Now safe to use in the prompt template
# #     system_prompt = f"""
# #     You are a Research Agent. Your task is to gather and analyze information based on the provided sections.

# #     Your job is to:
# #     - Collect factual news/articles/content ONLY.
# #     - NO analysis. NO opinion. NO rewriting into conclusions.
# #     - Extract only what exists in the content.

# #     You must extract:
# #     - Headlines
# #     - Summaries
# #     - Publication date
# #     - Outlet/source
# #     - Quotes by CXOs or important persons
# #     - Mentions of competitors
# #     - Mentions of the main entity
# #     - URLs

# #     **CRITICAL**: 
# #     - If no relevant information is found for a section, return an empty array in the "articles" field.
# #     - Ensure all data is accurate and verifiable.
# #     - Include URLs.
# #     - Do not generate any images or multimedia content.

# #     Output ONLY valid JSON following this exact schema:
# #     {schema_str}

# #     Return ONLY the JSON object with no additional text, markdown formatting, or code blocks.
# #     """

# #     human_prompt = """
# #     ### Sections to Research:
# #     {sections}

# #     ### User Intent:
# #     {intent}

# #     Return your response as a valid JSON object only.
# #     """

# #     prompt = ChatPromptTemplate.from_messages([
# #         ("system", system_prompt),
# #         ("human", human_prompt)
# #     ])

# #     messages = prompt.format_messages(
# #         sections=json.dumps(sections, indent=2),
# #         intent=intent
# #     )

# #     try:
# #         # Invoke the model
# #         tavily = TavilySearch(max_results=5)
# #         # raw_output = llm_no_tools.invoke(messages)
# #         raw_output  = tavily.invoke(messages)
# #         print("234565765654545477557888987857577",raw_output)
# #         output_text = raw_output.content.strip()
        
# #         # Remove markdown code blocks if present
# #         if output_text.startswith("```json"):
# #             output_text = output_text.replace("```json", "", 1)
# #         if output_text.startswith("```"):
# #             output_text = output_text.replace("```", "", 1)
# #         if output_text.endswith("```"):
# #             output_text = output_text.rsplit("```", 1)[0]
        
# #         output_text = output_text.strip()
        
# #         # Parse JSON
# #         json_data = json.loads(output_text)
       
# #         # Validate basic structure
# #         if "sections" not in json_data:
# #             return {
# #                 "error": "Invalid JSON structure - missing 'sections' key",
# #                 "raw": output_text
# #             }
        
# #         return json_data

# #     except json.JSONDecodeError as e:
# #         print(f"JSON decode error: {e}")
# #         return {
# #             "error": f"Invalid JSON from model: {str(e)}",
# #             "raw": output_text
# #         }
# #     except Exception as e:
# #         print(f"Unexpected error: {e}")
# #         return {
# #             "error": f"Unexpected error: {str(e)}",
# #             "raw": str(raw_output.content) if 'raw_output' in locals() else "No output"
# #         }


# import json
# from app.core.state import State
# from langchain_tavily import TavilySearch
# from app.agents.base_agent import llm_model
# from app.tools.research_tools import faiss_recall_tool, tavily_search_tool
# from app.tools.firecrawl_tool import parse_the_data
# from langgraph.prebuilt import create_react_agent

# def generate_search_query(section, intent):
#     """
#     Generates a concise, keyword-optimized search query based on the section scope and user intent.
#     """
#     system_prompt = """
#     You are a Search Query Optimizer.
#     Your task is to convert a research scope into a single, concise, keyword-rich search query.
    
#     RULES:
#     1. Output ONLY the search query string. No quotes, no explanations.
#     2. Keep it under 200 characters.
#     3. Focus on specific entities, topics, and keywords.
#     4. Remove instruction words like "Search for", "Find", "Extract", "Analyze".
#     """
    
#     user_prompt = f"""
#     ### Scope of Research:
#     {section.get('scope_of_research')}
    
#     ### Section Title:
#     {section.get('title')}
    
#     ### User Intent:
#     {intent}
    
#     Generate the best search query:
#     """
    
#     try:
#         response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
#         query = response.content.strip()
        
#         # Remove quotes if present
#         if query.startswith('"') and query.endswith('"'):
#             query = query[1:-1]
            
#         # Hard truncation safety net
#         if len(query) > 300:
#             query = query[:300]
            
#         return query
#     except Exception as e:
#         print(f"  -> Query Generation Error: {e}")
#         # Fallback
#         return f"{section.get('title')} {intent}"[:200]
# def research_agent(state: State = {}):
#     """
#     Research workflow:
#         1. Try FAISS recall.
#         2. If FAISS has results → RETURN DIRECTLY (NO PARSE, NO TAVILY).
#         3. If empty → run Tavily search.
#         4. Parse all Tavily URLs using parse_the_data.
#         5. Return structured research data for writer agent.
#     """

#     sections = state.get("sections", [])
#     intent = state.get("intent", "")

#     print("=== RESEARCH AGENT INPUT ===")
#     print(f"Total Sections: {len(sections)}")

#     # ----------------------------
#     # AGENT PROMPT (fallback logic)
#     # ----------------------------
#     prompt = """
#         You are a research agent. Follow the EXACT workflow:

#         STEP 1 — FAISS RECALL
#         - Use faiss_recall_tool first.
#         - If FAISS returns NON-EMPTY results (len > 0):
#             • Immediately return:
#                 [{"url": <faiss_url>}]
#             • DO NOT perform Tavily search.

#         STEP 2 — TAVILY SEARCH (only if FAISS empty)
#         - Use tavily_search_tool.
#         - The Tavily result will contain a list of URLs.

#         STEP 3 — PARSE (required for Tavily results)
#         - For EVERY URL returned by Tavily:
#             • Call parse_the_data

#         FINAL OUTPUT FORMAT (STRICT)
#         Must ALWAYS return a JSON list of objects in this exact format:

#         [
#             { "url": "https://example.com/page" },
#             { "url": "https://another.com/page" }
#         ]
#     """
    

#     # ----------------------------
#     # Create the Agent (correct!)
#     # ----------------------------
#     agent = create_react_agent(
#         model=llm_model,
#         tools=[faiss_recall_tool, tavily_search_tool, parse_the_data],
#         prompt=prompt
#     )

#     research_results = []

#     # ============================================================
#     # RUN FOR EACH SECTION
#     # ============================================================
#     for section in sections:
#         query = generate_search_query(section, intent)

#         print("\n=== Running Agent for Query ===")
#         print("QUERY:", query)

#         # Call the agent
#         response = agent.invoke(
#             {"messages": [{"role": "user", "content": query}]}
#         )
#         print("ressdfsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", response.content)
#         # # The last message is always the AIMessage
#         # last_msg = response.get("messages")[-1]
#         # content = last_msg.content.strip()
#         # print("content====================================", content)
#         for msg in response["messages"]:
#             if msg.__class__.__name__ == "ToolMessage":
#                 data = msg.content
#                 data = json.loads(data)
#                 print("data", data)
#                 results = data.get("results", [])

#                 for item in results:
#                     url = item.get("url")
#                     title = item.get("title")
#                     content = item.get("content")
#                     score = item.get("score")
#                     data = parse_the_data(url)
#                     research_results.append({
#                         "title": data.get("title"),
#                         "description": data.get("description"),
#                         "url": data.get("url"),
#                     })

#         # ============================================================
#         # PARSE EACH URL → FIRECRAWL
#         # ============================================================
#     state["research_data"] = research_results
#     return state


# def extract_data_with_llm(search_results, section, intent):
#     """
#     Helper function to extract structured data from raw search results using LLM.
#     """
    
#     system_prompt = """
#     You are a Research Extraction Agent.
#     Your task is to extract factual information from the provided search results.
    
#     EXTRACT:
#     - URLs
    
#     RULES:
#     1. Use ONLY the provided search results. Do NOT hallucinate.
#     2. If a result is irrelevant to the section topic, ignore it.
#     3. Return valid JSON only.
#     """
    
#     user_prompt = f"""
#     ### Section Goal:
#     {section.get('title')}
#     {section.get('scope_of_research')}
    
#     ### User Intent:
#     {intent}
    
#     ### Raw Search Results:
#     {json.dumps(search_results, indent=2, default=str)}
    
#     ### Output JSON Schema:
#     {{
#         "articles": [
#             {{
#                 "headline": "string",
#                 "summary": "string",
#                 "publication_date": "string",
#                 "source": "string",
#                 "url": "string",
#                 "quotes": ["string"]
#             }}
#         ]
#     }}
#     """
    
#     try:
#         response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
#         content = response.content.strip()
        
#         # Clean up code blocks if present
#         if content.startswith("```json"):
#             content = content.replace("```json", "", 1)
#         if content.startswith("```"):
#             content = content.replace("```", "", 1)
#         if content.endswith("```"):
#             content = content.rsplit("```", 1)[0]
            
#         return json.loads(content.strip())
        
#     except Exception as e:
#         print(f"  -> Extraction Error: {e}")
#         return {"articles": []}


# def generate_search_query(section, intent):
#     """
#     Generates a concise, keyword-optimized search query based on the section scope and user intent.
#     """
#     system_prompt = """
#     You are a Search Query Optimizer.
#     Your task is to convert a research scope into a single, concise, keyword-rich search query.
    
#     RULES:
#     1. Output ONLY the search query string. No quotes, no explanations.
#     2. Keep it under 200 characters.
#     3. Focus on specific entities, topics, and keywords.
#     4. Remove instruction words like "Search for", "Find", "Extract", "Analyze".
#     """
    
#     user_prompt = f"""
#     ### Scope of Research:
#     {section.get('scope_of_research')}
    
#     ### Section Title:
#     {section.get('title')}
    
#     ### User Intent:
#     {intent}
    
#     Generate the best search query:
#     """
    
#     try:
#         response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
#         query = response.content.strip()
        
#         # Remove quotes if present
#         if query.startswith('"') and query.endswith('"'):
#             query = query[1:-1]
            
#         # Hard truncation safety net
#         if len(query) > 300:
#             query = query[:300]
            
#         return query
#     except Exception as e:
#         print(f"  -> Query Generation Error: {e}")
#         # Fallback
#         return f"{section.get('title')} {intent}"[:200]
import json
from app.core.state import State
from app.agents.base_agent import llm_model
from app.tools.research_tools import faiss_recall_tool, tavily_search_tool
from app.tools.firecrawl_tool import parse_the_data
from langgraph.prebuilt import create_react_agent


def generate_search_query(section, intent):
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
        response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
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


def research_agent(state: State = {}):
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
        tools=[faiss_recall_tool, tavily_search_tool, parse_the_data],
        prompt=prompt
    )

    research_results = []

    for section in sections:
        query = generate_search_query(section, intent)

        print("\n=== Running Agent for Query ===")
        print("QUERY:", query)

        response = agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        for msg in response["messages"]:
            if msg.__class__.__name__ == "ToolMessage":
                tool_name = msg.name
                
                print(f"\n=== Processing {tool_name} ===")
                
                try:
                        content = msg.content
                        
                        if content is None or content == "null":
                            print("Tavily returned null, skipping...")
                            continue
                        
                        data = json.loads(content)
                        
                        if data is None:
                            print("Tavily data is None, skipping...")
                            continue
                        
                        # Get results - handle both list and dict formats
                        if isinstance(data, list):
                            results = data
                        elif isinstance(data, dict):
                            results = data.get("results", [])
                        else:
                            print(f"Unexpected Tavily data type: {type(data)}")
                            continue
                        
                        print(f"Found {len(results)} Tavily results")
                        
                        # Process each result
                        for item in results:
                            url = item.get("url")
                            if not url:
                                print("Skipping item without URL")
                                continue
                            
                            print(f"Parsing URL: {url}")
                            
                            try:
                                # Parse the URL content
                                parsed_data = parse_the_data(url)
                                print("parsed data", parsed_data)
                                research_results.append({
                                    "title": parsed_data.get("title", ""),
                                    "description": parsed_data.get("description", ""),
                                    "url": parsed_data.get("url", url),
                                })
                            except Exception as parse_error:
                                print(f"Error parsing {url}: {parse_error}")
                                continue
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error for Tavily result: {e}")
                    print(f"Content was: {content}")
                    continue
                except Exception as e:
                    print(f"Unexpected error processing Tavily result: {e}")
                    continue

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