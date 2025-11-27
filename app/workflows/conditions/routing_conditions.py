from app.core.state import State


def should_clarification_is_needed(state: State = {}):
    needs_clarification = state.get("needs_clarification", False)

    if needs_clarification:
        return "clarification_node"
    return "planner_decision"