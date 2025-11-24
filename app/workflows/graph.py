from app.agents.research_agent import research_agent
from app.workflows.conditions.routing_conditions import should_clarification_is_nedded
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from app.agents.planner_agent import planner_agent
from app.agents.writer_agent import writer_agent
from app.agents.intent_agent import intent_agent
from app.workflows.nodes.clarification_node import clarification_node
from app.core.state import State
graph = StateGraph(State)

graph.add_node("intent_agent", intent_agent)
graph.add_node("planner_decision", planner_agent)
graph.add_node("clarification_node",clarification_node )
graph.add_node("research_agent", research_agent)
graph.add_node("writer_agent", writer_agent)

graph.add_edge(START, "intent_agent")
graph.add_conditional_edges(
    "intent_agent",                     # <-- source node
    should_clarification_is_nedded,     # <-- condition function
    {
        "clarification_node": "clarification_node",
        "planner_decision": "planner_decision"
    }
)
graph.add_edge("planner_decision", "research_agent")
graph.add_edge("research_agent", "writer_agent")
graph.add_edge("writer_agent", END)

app = graph.compile()
print(app)
display(Image(app.get_graph().draw_mermaid_png()))