import json
from datetime import datetime
from typing import Any, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.state import State
from app.agents.base_agent import llm_model
from langgraph.prebuilt import create_react_agent


def planner_agent(state: State = {}):
    user_intent = state.get("intent", "")
    print("========================planner INPUT========================", user_intent)

    system_prompt = f"""
    You are the Planning and Delegation Lead for a news intelligence system.
    Your job is to create detailed, realistic, and hallucination-free research plans based on user intent.

    CRITICAL: Today's date is {datetime.now().strftime('%Y-%m-%d')}. Use this for calculating time ranges.

    ### AVAILABLE AGENTS & THEIR CAPABILITIES:
    **Researcher Agent**:
    - Collects news articles from vector databases (indexed sources) and web search
    - Extracts: headlines, outlets, dates, URLs, authors, summaries
    - Identifies: CXO mentions, competitor mentions, product mentions, trends
    - CANNOT: Create images, charts, or visual content
    - Best for: Data gathering, article collection, information retrieval

    **Writer Agent**:
    - Analyzes and synthesizes existing research data
    - Creates: reports, summaries, insights, risk assessments
    - Performs: comparative analysis, trend identification, narrative synthesis
    - CANNOT: Access databases directly, generate images/charts, search the web
    - Best for: Analysis, synthesis, report generation, strategic insights

    ### STRICT ANTI-HALLUCINATION RULES:
    1. **NO INVENTED DATA**: Do NOT create fictional article titles, specific facts, or data points
    2. **NO SPECIFIC SOURCES**: Do NOT list specific URLs, outlet names, or author names unless explicitly provided by user
    3. **REALISTIC TARGETS**: Base articles_target on reasonable expectations (10-50 articles typically)
    4. **NO VISUALS**: Do NOT plan for images, charts, diagrams - text-based deliverables ONLY
    5. **GROUNDED SCOPE**: Define what to search for (keywords, topics, entities) without promising specific results

    ### SECTION TYPES (CRITICAL DISTINCTION):
    **"research"** sections:
    - Purpose: NEW data collection from sources
    - Required: Populate "scope_of_research" with detailed collection objectives
    - Leave "scope_of_analysis" empty or null

    **"analysis"** sections:
    - Purpose: Synthesize and analyze EXISTING collected data
    - Required: Populate "scope_of_analysis" with specific analytical instructions
    - Leave "scope_of_research" empty or null
    - Set articles_target to 0
    - Example scope: "Analyze sentiment trends in collected articles, identify recurring themes, assess competitive positioning, and evaluate potential crisis indicators."

    ### PLANNING GUIDELINES:
    - Create at least 1 section, but don't over-plan for simple queries
    - Each section must have a clear, achievable objective
    - Match coverage_type to the actual content (company_news, competitors, risks_crisis, policy, cxo_mentions, landscape, narrative, analysis)
    - Only include competitors if mentioned by user or directly relevant
    - Time ranges should be realistic and based on today's date
    """


    user_prompt = """
        ### User Intent:
        {intent}

        ### Output JSON Schema:
        {
            "user_confirmation_message": "Clear, concise message summarizing the plan",
            "sections": [
                {
                    "title": "Descriptive title for this section",
                    "time_range": {
                        "start": "YYYY-MM-DD",
                        "end": "YYYY-MM-DD"
                    },
                    "plan": "High-level description in markdown format explaining what this section will accomplish",
                    "scope_of_research": "REQUIRED for 'research' sections. Detailed instructions: what keywords to search, what entities to focus on, what data points to extract.,
                    "scope_of_analysis": "REQUIRED for 'analysis' sections. Specific analytical tasks: what questions to answer, what patterns to identify, what insights to generate.,
                    "coverage_type": "company_news|competitors|risks_crisis|policy|cxo_mentions|landscape|narrative|analysis",
                    "coverage_scope": "global",
                    "competitors": ["Only list if explicitly mentioned by user or directly relevant, otherwise empty array"],
                    "tone": "neutral|executive|technical",
                    "length": "brief|standard|deep-dive",
                    "languages": ["en"],
                    "articles_target": "Number between 10-50 for research sections, 0 for analysis sections",
                    "section_type": "research|analysis"
                }
            ]
        }
        Important: Return ONLY a JSON object. No extra commentary.
        """
    format_instructions = """
        {
            "user_confirmation_message": "Clear, concise message summarizing the plan",
            "sections": [
                {
                    "title": "Descriptive title for this section",
                    "time_range": {
                        "start": "YYYY-MM-DD",
                        "end": "YYYY-MM-DD"
                    },
                    "plan": "High-level description in markdown format explaining what this section will accomplish",
                    "scope_of_research": "REQUIRED for 'research' sections. Detailed instructions: what keywords to search, what entities to focus on, what data points to extract.,
                    "scope_of_analysis": "REQUIRED for 'analysis' sections. Specific analytical tasks: what questions to answer, what patterns to identify, what insights to generate.,
                    "coverage_type": "company_news|competitors|risks_crisis|policy|cxo_mentions|landscape|narrative|analysis",
                    "coverage_scope": "global",
                    "competitors": ["Only list if explicitly mentioned by user or directly relevant, otherwise empty array"],
                    "tone": "neutral|executive|technical",
                    "length": "brief|standard|deep-dive",
                    "languages": ["en"],
                    "articles_target": "Number between 10-50 for research sections, 0 for analysis sections",
                    "section_type": "research|analysis"
                }
            ]
        }

    **FIELD GUIDELINES**:
    - scope_of_research: For 'research' sections ONLY. Define search parameters, keywords, entities, data extraction requirements
    - scope_of_analysis: For 'analysis' sections ONLY. Define analytical questions, metrics to calculate, insights to derive
    - articles_target: Realistic number (10-50) for research; 0 for analysis
    - section_type: 'research' = data collection, 'analysis' = data synthesis
    """

    agent = create_react_agent(
        model=llm_model,
        tools=[],
        prompt=system_prompt
   )
    response = agent.invoke(
      {"messages": [{"role": "user", "content": user_prompt}]}
    )
    print("INTENT RESPONSE=========================", response)
    try:
        for msg in response["messages"]:
            if msg.__class__.__name__ == "AIMessage":
                content = msg.content
   
    
    # Parse JSON safely with better error handling
        json_data = json.loads(content)
        
        # Validate essential fields
        if "sections" not in json_data or not json_data["sections"]:
            print("Warning: No sections in plan, creating default section")
            json_data["sections"] = [{
                "title": "Research Plan",
                "time_range": {"start": datetime.now().strftime('%Y-%m-%d'), "end": datetime.now().strftime('%Y-%m-%d')},
                "plan": "Default research section",
                "scope_of_research": user_intent,
                "scope_of_analysis": "",
                "coverage_type": "company_news",
                "coverage_scope": "global",
                "competitors": [],
                "tone": "neutral",
                "length": "standard",
                "languages": ["en"],
                "articles_target": 20,
                "section_type": "research"
            }]
        
        print("sections", json_data.get("sections"))
        state['sections'] = json_data.get("sections")
        state['time_range'] = state['sections'][0].get("time_range", None) if state['sections'] else None
        print("========================planner OUTPUT========================")
        print(json_data)
        
        return state
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw output: {response}")
        return {"error": "Invalid JSON from model", "raw": response, "json_error": str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error processing plan", "raw": response, "exception": str(e)}

