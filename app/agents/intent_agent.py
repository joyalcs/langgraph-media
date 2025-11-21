import json
from app.core.state import State
from app.agents.base_agent import llm_model


def intent_agent(state: State = {}):
    system_prompt = """
        You are an Intent Detection Agent.
        Your job is to:
            1. Identify the user's intent.
            2. Decide if the query is incomplete or ambiguous.
            3. If incomplete, describe what information is missing.

        INTENT CATEGORIES:
        - "media_info" → movies, actors, news about celebrities, cast, music, entertainment
        - "search" → general information lookup
        - "recommendation" → ask for suggestions (movies, songs, content)
        - "fact_lookup" → asking a direct factual question
        - "news" → user wants the latest updates
        - "unknown" → cannot determine

        Response MUST be valid JSON ONLY:
        {
            "intent": "...",
            "needs_clarification": true/false,
            "missing_information": "If clarification needed, explain what is missing, else empty string",
            "findings": "Provide a brief summary of your analysis"
        }    
    """
    user_prompt = f"""User Message: {state.get("user_message", "")}"""

    response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
    data = json.loads(response.content)
    print("Intent Agent Response:", response)
    state["intent"] = data["findings"]
    state["needs_clarification"] = data["needs_clarification"]
    state["missing_information"] = data["missing_information"]
    return state
    