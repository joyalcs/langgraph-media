import json
from app.core.state import State
from app.agents.base_agent import llm_model


def intent_agent(state: State = {}):
    system_prompt = """
        You are an Intent Detection Agent for a media application.
        Your job is to analyze the user's message and identify their intent with high precision.

        INTENT CATEGORIES:
        1. "media_info":
           - User asks about movies, TV shows, actors, directors, cast, plot, release dates, ratings, or news about celebrities.
           - Examples: "Who directed Inception?", "Tell me about Tom Cruise", "What is the plot of The Matrix?", "Latest news on Marvel movies".

        2. "search":
           - General information lookup that doesn't fit strictly into media info, or broad searches.
           - Examples: "Search for best sci-fi books", "Information about space travel".

        3. "recommendation":
           - User explicitly asks for suggestions or recommendations for content (movies, music, books, etc.).
           - Examples: "Suggest some good horror movies", "What should I watch tonight?", "Recommend me a song like this".

        4. "fact_lookup":
           - User asks a direct factual question that expects a specific answer (often non-media related or general knowledge).
           - Examples: "What is the capital of France?", "How tall is Mount Everest?".

        5. "news":
           - User specifically wants the latest updates, headlines, or current events (can be general or specific topics).
           - Examples: "What's happening in the world today?", "Latest tech news".

        6. "unknown":
           - The user's intent is unclear, ambiguous, or consists of chitchat/greetings (e.g., "Hello", "Hi", "How are you?").
           - Use this if the query doesn't fit any of the above categories.

        INSTRUCTIONS:
        1. Analyze the user's message carefully.
        2. Assign the most appropriate category from the list above.
        3. Determine if the query is incomplete or ambiguous ("needs_clarification").
        4. If incomplete, describe exactly what information is missing in "missing_information".
        5. Provide a brief summary of your analysis in "findings".

        Response MUST be valid JSON ONLY:
        {
            "intent": "Brief summary of analysis and maximum 200 characters",
            "needs_clarification": true/false,
            "missing_information": "If clarification needed, explain what is missing, else empty string",
            "findings": "Brief summary of analysis"
        }
    """
    user_prompt = f"""User Message: {state.get("user_message", "")}"""

    response = llm_model.invoke(system_prompt + "\n\n" + user_prompt)
    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback if JSON is invalid
        print("Error decoding JSON response:", response.content)
        data = {
            "intent": "unknown",
            "needs_clarification": False,
            "missing_information": "",
            "findings": "Error processing request"
        }

    print("Intent Agent Response:", data)
    state["intent"] = data["findings"]
    state["needs_clarification"] = data["needs_clarification"]
    state["missing_information"] = data["missing_information"]
    return state