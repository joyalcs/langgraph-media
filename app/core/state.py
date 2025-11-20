from typing import TypedDict, List, Optional, Literal
class State(TypedDict):
    user_message: str
    intent: str
    needs_clarification: bool 
    missing_information: str