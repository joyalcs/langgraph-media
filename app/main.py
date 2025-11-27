from fastapi import FastAPI, Form
from typing import Optional
from app.workflows.graph import app as graph_app  # LangGraph instance

app = FastAPI()

@app.post("/")
async def run_graph(
    user_message: Optional[str] = Form(None),
    payload: Optional[dict] = None
):
    # If JSON payload is sent
    if payload and "user_message" in payload:
        user_message = payload["user_message"]

    # If neither provided
    if not user_message:
        return {"error": "user_message is required"}

    result = await graph_app.ainvoke({
        "user_message": user_message
    })
    return result
