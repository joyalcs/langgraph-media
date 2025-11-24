# import json
# from app.core.state import State
# from app.agents.base_agent import llm_model
# from langchain_core.prompts import ChatPromptTemplate
from app.tools.firecrawl_tool import parse_the_data
from langchain_groq import ChatGroq
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_tavily import TavilySearch

llm_no_tools = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# def research_agent(state: State = {}):
#     sections = state.get('sections', [])
#     print("========================research_agent INPUT========================", sections)
    
#     intent = state.get('intent', '')
    
#     # Define JSON schema for structured output
#     json_schema = {
#         "type": "object",
#         "properties": {
#             "sections": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "section_name": {"type": "string"},
#                         "articles": {
#                             "type": "array",
#                             "items": {
#                                 "type": "object",
#                                 "properties": {
#                                     "headline": {"type": "string"},
#                                     "summary": {"type": "string"},
#                                     "publication_date": {"type": "string"},
#                                     "source": {"type": "string"},
#                                     "url": {"type": "string"},
#                                     "quotes": {"type": "array", "items": {"type": "string"}},
#                                     "competitors_mentioned": {"type": "array", "items": {"type": "string"}},
#                                     "entity_mentions": {"type": "array", "items": {"type": "string"}}
#                                 },
#                                 "required": ["headline", "summary", "publication_date", "source", "url"]
#                             }
#                         }
#                     },
#                     "required": ["section_name", "articles"]
#                 }
#             }
#         },
#         "required": ["sections"]
#     }
    
#     # Convert schema to string and escape curly braces for f-string
#     schema_str = json.dumps(json_schema, indent=2).replace("{", "{{").replace("}", "}}")
    
#     # Now safe to use in the prompt template
#     system_prompt = f"""
#     You are a Research Agent. Your task is to gather and analyze information based on the provided sections.

#     Your job is to:
#     - Collect factual news/articles/content ONLY.
#     - NO analysis. NO opinion. NO rewriting into conclusions.
#     - Extract only what exists in the content.

#     You must extract:
#     - Headlines
#     - Summaries
#     - Publication date
#     - Outlet/source
#     - Quotes by CXOs or important persons
#     - Mentions of competitors
#     - Mentions of the main entity
#     - URLs

#     **CRITICAL**: 
#     - If no relevant information is found for a section, return an empty array in the "articles" field.
#     - Ensure all data is accurate and verifiable.
#     - Include URLs.
#     - Do not generate any images or multimedia content.

#     Output ONLY valid JSON following this exact schema:
#     {schema_str}

#     Return ONLY the JSON object with no additional text, markdown formatting, or code blocks.
#     """

#     human_prompt = """
#     ### Sections to Research:
#     {sections}

#     ### User Intent:
#     {intent}

#     Return your response as a valid JSON object only.
#     """

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", human_prompt)
#     ])

#     messages = prompt.format_messages(
#         sections=json.dumps(sections, indent=2),
#         intent=intent
#     )

#     try:
#         # Invoke the model
#         tavily = TavilySearch(max_results=5)
#         # raw_output = llm_no_tools.invoke(messages)
#         raw_output  = tavily.invoke(messages)
#         print("234565765654545477557888987857577",raw_output)
#         output_text = raw_output.content.strip()
        
#         # Remove markdown code blocks if present
#         if output_text.startswith("```json"):
#             output_text = output_text.replace("```json", "", 1)
#         if output_text.startswith("```"):
#             output_text = output_text.replace("```", "", 1)
#         if output_text.endswith("```"):
#             output_text = output_text.rsplit("```", 1)[0]
        
#         output_text = output_text.strip()
        
#         # Parse JSON
#         json_data = json.loads(output_text)
       
#         # Validate basic structure
#         if "sections" not in json_data:
#             return {
#                 "error": "Invalid JSON structure - missing 'sections' key",
#                 "raw": output_text
#             }
        
#         return json_data

#     except json.JSONDecodeError as e:
#         print(f"JSON decode error: {e}")
#         return {
#             "error": f"Invalid JSON from model: {str(e)}",
#             "raw": output_text
#         }
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return {
#             "error": f"Unexpected error: {str(e)}",
#             "raw": str(raw_output.content) if 'raw_output' in locals() else "No output"
#         }


import json
from app.core.state import State
from langchain_tavily import TavilySearch
from app.agents.base_agent import llm_model

def research_agent(state: State = {}):
    sections = state.get("sections", [])
    intent = state.get("intent", "")
    
    print("=== RESEARCH AGENT INPUT ===")
    print(f"Total Sections: {len(sections)}")

    # Initialize Tavily client
    tavily = TavilySearch(max_results=5)
    
    research_results = []
    
    # Filter for RESEARCH sections only
    research_sections = [s for s in sections if s.get("section_type") == "research"]
    
    if not research_sections:
        print("No research sections found. Skipping research phase.")
        return state

    for section in research_sections:
        print(f"Processing Section: {section.get('title')}")
        
        # Generate optimized search query using LLM
        query = generate_search_query(section, intent)
            
        print(f"  -> Search Query: {query}")

        try:
            # Execute Search
            search_output = tavily.invoke({"query": query})
            
            # Check for search errors or empty results
            if isinstance(search_output, dict) and "error" in search_output:
                print(f"  -> Search API Error: {search_output['error']}")
                research_results.append({
                    "section_title": section.get("title"),
                    "error": search_output['error'],
                    "articles": []
                })
                continue
            # Extract structured data using LLM
            extracted_data = extract_data_with_llm(search_output, section, intent)
            extracted_articles = extracted_data.get("articles", [])
            for extracted_article in extracted_articles:
                data = parse_the_data(extracted_article.get("url"))
                research_results.append({
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "url": data.get("url"),
                })
            
        except Exception as e:
            print(f"  -> Error in section '{section.get('title')}': {e}")
            research_results.append({
                "section_title": section.get("title"),
                "error": str(e),
                "articles": []
            })
            
    # Update state with research results
    # We append to existing research_data if any, or create new
    current_data = state.get("research_data", [])
    if isinstance(current_data, list):
        state["research_data"] = current_data + research_results
    else:
        state["research_data"] = research_results
        
    print("=== RESEARCH AGENT COMPLETE ===")
    return state


def extract_data_with_llm(search_results, section, intent):
    """
    Helper function to extract structured data from raw search results using LLM.
    """
    
    system_prompt = """
    You are a Research Extraction Agent.
    Your task is to extract factual information from the provided search results.
    
    EXTRACT:
    - Headlines
    - Summaries (concise, factual)
    - Publication Dates (YYYY-MM-DD if available)
    - Sources/Outlets
    - URLs
    - Key Quotes (especially from executives/officials)
    
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
