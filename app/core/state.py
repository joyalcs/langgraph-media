from typing import Any, Dict, TypedDict, List, Optional, Literal
class State(TypedDict):
    user_message: str
    intent: str
    needs_clarification: bool 
    missing_information: str
    sections: List
    time_range: Dict
    coverage_type: Optional[Literal["company news", "competitors", "risks/crisis", "policy", "CXO mentions", "landscape", "narrative", "analysis"]]
    tone: Optional[Literal["neutral", "executive", "technical"]]
    research_data: List