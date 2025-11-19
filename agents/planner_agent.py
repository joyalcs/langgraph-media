import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


async def planner_descision_agent(user_message: str) -> Dict[str, Any]:
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
