# LangGraph Media

**LangGraph Media** is a sophisticated multi-agent system designed to automate the process of research and content creation. Leveraging the power of **LangGraph**, **FastAPI**, and advanced LLMs, this project orchestrates a team of AI agents to understand user intent, plan research strategies, gather information from the web, and synthesize high-quality content.

## 🚀 Features

-   **Intent Analysis**: Intelligently parses user requests to determine the best course of action.
-   **Automated Planning**: Decomposes complex topics into actionable research steps.
-   **Deep Web Research**: Utilizes **Tavily** and **Firecrawl** to gather comprehensive and relevant data from the web.
-   **Intelligent Caching**: Implements **FAISS** for efficient vector-based storage and retrieval of research findings.
-   **Content Generation**: Synthesizes research into well-structured, engaging written content.
-   **Interactive Workflow**: Built on **LangGraph** to manage state and agent interactions seamlessly.

## 🏗️ Architecture

The system is built upon a modular architecture comprising specialized agents:

-   **Intent Agent**: The entry point that analyzes the user's request.
-   **Planner Agent**: Formulates a detailed plan based on the user's intent.
-   **Research Agent**: Executes the plan by searching the web and processing information.
-   **Writer Agent**: Compiles the gathered information into the final output.

These agents collaborate within a **LangGraph** state machine, ensuring a robust and observable workflow.

## 🛠️ Installation

### Prerequisites

-   Python 3.10 or higher
-   [API Keys] for:
    -   OpenAI (or compatible LLM provider)
    -   Tavily
    -   Firecrawl
    -   Groq (optional, if used)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/joyalcs/langgraph-media.git
    cd langgraph-media
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your API keys:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    TAVILY_API_KEY=your_tavily_api_key
    FIRECRAWL_API_KEY=your_firecrawl_api_key
    GROQ_API_KEY=your_groq_api_key
    ```

## 🏃 Usage

1.  **Start the Application:**
    Run the FastAPI server using Uvicorn:
    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Trigger the Workflow:**
    You can interact with the API via the Swagger UI at `http://127.0.0.1:8000/docs` or send a POST request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/' \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -d 'user_message=Research the latest advancements in solid state batteries'
    ```

## 📂 Project Structure

```
langgraph-media/
├── app/
│   ├── agents/         # Agent implementations (Intent, Planner, Research, Writer)
│   ├── core/           # Core logic and state definitions
│   ├── tools/          # External tools (Firecrawl, Tavily, etc.)
│   ├── workflows/      # LangGraph workflow definitions
│   └── main.py         # FastAPI entry point
├── vectorstore/        # FAISS index storage
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
