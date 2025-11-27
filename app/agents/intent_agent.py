import json
from app.core.state import State
from app.agents.base_agent import llm_model
from datetime import datetime, timedelta
from langgraph.prebuilt import create_react_agent
def intent_agent(state: State = {}):
   today = datetime.now().date()
   thirty_days_ago = today - timedelta(days=30)
    
   system_prompt = f"""
        You are an Intent Detection Agent for a media and automotive application.
        Your job is to analyze the user's message and identify their intent with high precision.
        CRITICAL INSTRUCTIONS:
        1. Analyze the user's message carefully.
        2. Assign the most appropriate category from the list above.
        3. For automotive queries, DO NOT ask for clarification on year/color/variant - provide latest model info.
        4. ONLY set needs_clarification=true if the core request is genuinely unclear or ambiguous.
        5. The "findings" field should be a brief analysis summary (max 200 chars), NOT a statement to the user.
        6. If date range is not provided, use last 30 days as date range (from {thirty_days_ago} to {today}).
        7. If region is not specified, assume region as "global".
   
        RESPONSE FORMAT:
        You MUST respond with ONLY valid JSON in this EXACT structure. Do not add any other text.
        
        {{
            "intent": "<dynamically determined intent category - be specific and descriptive>
            "needs_clarification": <true or false boolean>,
            "missing_information": "<specific missing info OR empty string if none>",
            "findings": "<brief internal analysis summary, maximum 200 characters>"
        }}
    """
   user_prompt = f"""User Message: {state.get("user_message", "")}"""
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
   
      data = json.loads(content)
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