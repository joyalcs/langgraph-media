from app.agents.base_agent import llm_model
from app.core.state import State
def clarification_node(state: State) -> str:
    """
    A simple clarification node that asks the user for more information.
    """
    clarification_prompt = f"""
    The user's message is: "{state.get('user_message', '')}"

    It seems that the message is ambiguous or incomplete. Could you please provide more details or clarify your intent?
    """
    response =  llm_model.invoke(clarification_prompt)
    print("Clarification Node Response:", response)
    return {
        "clarification_question": response.content
    }
