# import json
# from app.core.state import State
# from app.agents.base_agent import llm_model
# from langchain_core.prompts import ChatPromptTemplate
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
from app.core.state import State  # LLM without tools
from langchain_tavily import TavilySearch

# --------------------------
# Research Agent
# --------------------------

def research_agent(state: State = {}):
    sections = state.get("sections", [])
    intent = state.get("intent", "")

    print("=== RESEARCH AGENT INPUT ===", sections)

    # Initialize Tavily client
    tavily = TavilySearch(max_results=5)

    # ---------------------------------------
    # STEP 1: Run Tavily search for each section
    # ---------------------------------------
    tavily_results = []

    for section in sections:
        query = section.get("title") or section.get("name") or section.get("query") or str(section)

        try:
            search_output = tavily.invoke({"query": query})
            tavily_results.append({
                "section_name": query,
                "raw_search_results": search_output
            })

        except Exception as e:
            print("Tavily error:", e)
            tavily_results.append({
                "section_name": query,
                "raw_search_results": []
            })

    # ---------------------------------------
    # STEP 2: Ask the LLM to extract structured JSON
    # ---------------------------------------

    extraction_system_prompt = """
You are a Research Extraction Agent.

You will receive:
- A list of sections
- Tavily search results for each section

Your task:
- Extract ONLY factual information found in search results.
- For each article, extract:

  - headline
  - summary
  - publication_date
  - source
  - url
  - quotes (array)
  - competitors_mentioned (array)
  - entity_mentions (array)

Rules:
- If a section has no results → articles = []
- DO NOT hallucinate.
- DO NOT fabricate missing data.
- Use only what appears in search results.
- Output ONLY raw JSON (no text, no commentary).

JSON schema:
{
  "sections": [
    {
      "section_name": "string",
      "articles": [
        {
          "headline": "string",
          "summary": "string",
          "publication_date": "string",
          "source": "string",
          "url": "string",
          "quotes": ["string"],
          "competitors_mentioned": ["string"],
          "entity_mentions": ["string"]
        }
      ]
    }
  ]
}
"""

    extraction_user_prompt = f"""
Extract facts from the following Tavily search results:

{json.dumps(tavily_results, indent=2)}

INTENT: {intent}

Return ONLY valid JSON following the schema.
"""

    llm_output = llm_no_tools.invoke([
        {"role": "system", "content": extraction_system_prompt},
        {"role": "user", "content": extraction_user_prompt},
    ])

    text = llm_output.content.strip()

    # remove accidental code fences
    if text.startswith("```"):
        text = text.strip("`")
    if text.startswith("json"):
        text = text.replace("json", "", 1)

    # ---------------------------------------
    # STEP 3: Parse JSON from the LLM
    # ---------------------------------------
    try:
        parsed = json.loads(text)

        if "sections" not in parsed:
            return {
                "error": "Invalid JSON - missing 'sections'",
                "raw": text
            }

        return parsed

    except Exception as e:
        print("JSON parse error:", e)
        return {
            "error": "Failed to parse LLM output",
            "raw": text
        }
