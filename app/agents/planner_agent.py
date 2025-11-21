import json
from datetime import datetime
from typing import Any, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.state import State
from app.agents.base_agent import llm_model


def planner_descision_agent(user_message: str) -> Dict[str, Any]:
    system_prompt = """You are a message descision making agent. your task is to analyze the user's message and determine the appropriate action to take. You have access to the following tools:
    1. APPROVE: When user is approving/confirming message is appropriate and does not violate any guidelines.
    2. MODIFICATION: When user wants to modify the message to make it appropriate.
    3. APPROVED_EXTEND: When user is unsure about the message and needs human review.
    
    Analyze the user message and classify it accurately."""

    user_prompt = f"""User Message: {user_message}"

    Classify this message and provide your analysis in the following JSON format:
    {{
        "action": "APPROVE" | "MODIFICATION" | "APPROVED_EXTEND",
        "confidence": float (0.0 to 1.0),
        "reasoning": "string explaining the reasoning behind the decision"
    }}
    Important: Return ONLY a valid JSON object. No additional text.
    """

    raw = llm_model.invoke(system_prompt + "\n\n" + user_prompt)

    # Convert to dict safely
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "Invalid JSON from model", "raw": raw}


def planner_agent(state: State = {}):
    user_intent = state.get("intent", "")
    print("========================planner INPUT========================", user_intent)

    system_prompt = f"""
    You are the planning and delegation agent. Your job is to create a detailed plan based on the user's intent for gathering and analyzing.
    You can create multiple sections based on the user query and the entity/company if required.

    Your job is to:
    1. Understand the user's intent.
    2. Convert this intent into a structured NEWS-INTELLIGENCE PLAN.
    3. Output ONLY the JSON object following the schema.

    CRITICAL: Today's date is {datetime.now().strftime('%Y-%m-%d')}. you can use this information for time ranges in the plan.
    ### Agent Capabilities:
    - You can create multiple sections for different aspects of the research and analysis.
    - Each section should have a clear plan, scope of research, and analysis.
    - Identifies the type of coverage needed (company news, competitors, risks/crisis, policy, CXO mentions, landscape, narrative, analysis).
    - Best for - data collection, trend analysis, competitive intelligence, risk assessment, market research.
    ### Writer Agent:
    - Focuses on drafting high-quality content based on the plan.
    - Uses the research and analysis provided by the Researcher Agent.
    - Best for - content creation, report writing, executive summaries, detailed articles.
    ### Confirmation Agent:
    - Confirms the plan with the user before execution.
    - Ensures the plan aligns with user expectations and requirements.
    - Ensures the collected data meets quality standards.
    - Best for - user validation, quality assurance, feedback incorporation.

    RULES:
    - sections MUST contain at least 1 section.
    - Do not leave sections empty.
    - Do not hallucinate.
    - All deliverables must be text-based: reports, summaries, analysis, written insights

   
    """


    human_prompt = """
        ### User Intent:
        {intent}

        ### Output JSON Schema:
        {format_instructions}

        Important: Return ONLY a JSON object. No extra commentary.
        """
    format_instructions = """
        {
            "user_confirmation_message": "string",
            "sections": [
                {
                    "title": "title of the section",
                    "time_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
                    "plan": "markdown high-level plan for this section",
                    "scope_of_research": "identify all news articles mentioning [entity], extract headlines, summaries, dates, outlets, CXO quotes, competitor mentions",
                    "scope_of_analysis": "analyze sentiment trends, key themes, competitive positioning, crisis indicators",
                    "coverage_type": "company_news|competitors|risks_crisis|policy|cxo_mentions|landscape|narrative|analysis",
                    "coverage_scope": "global",
                    "competitors": [],
                    "tone": "neutral|executive|technical",
                    "length": "brief|standard|deep-dive",
                    "languages": ["en"],
                    "articles_target": 10,
                    "section_type": "research|analysis"
                }
            ]
        }

    **SCOPE FIELD GUIDELINES**:
        - scope_of_research (for research sections): What data to find, where to look, what to extract
         - scope_of_analysis (for analysis sections): What to analyze, what insights to generate, what patterns to identify, how to synthesize findings
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ]).partial(format_instructions=format_instructions)

    messages = prompt.format_messages(intent=user_intent)
    raw_output = llm_model.invoke(messages)

    output_text = raw_output.content if hasattr(raw_output, "content") else str(raw_output)
    json_data =json.loads(output_text)
    print("sections", json_data.get("sections"))
    state['sections'] = json_data.get("sections",)
    state['time_range'] = state['sections'][0].get("time_range", None) if state['sections'] else None
    print("========================planner OUTPUT========================")
    print(json_data)
    
    # 🟢 Parse JSON safely
    try:
        return state
    except Exception:
        return {"error": "Invalid JSON from model", "raw": output_text}
