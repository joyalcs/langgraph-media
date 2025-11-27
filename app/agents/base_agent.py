from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
llm_model = lm = ChatOpenAI(model="gpt-5-nano", temperature=0.3)
    # from datetime import datetime
    # import json
    # from typing import Any, Dict
    
    # from langchain.agents import AgentExecutor, create_tool_calling_agent
    # from langchain_core.messages import AIMessage, HumanMessage
    # from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    # from agents.base_agents import base_llm,base_reasoning_llm
    # from utils.data_helpers import trim_articles
    # from core.state import State
    # from config.settings import DEBUG_MODE
    # from utils.helpers import extract_json_from_llm_response
    
    # async def planner_classifier_agent(user_message: str) -> Dict[str, Any]:
    
    #     system_prompt = """You are a message classifier for a planning system.
    #     Your job is to analyze user messages and determine if they are:
    #     1. APPROVAL: User is approving/confirming the current plan WITHOUT any modifications (e.g., "yes", "approve", "ok", "done", "go ahead", "continue", "proceed", "confirmed", "looks good", "perfect", "let's do it")
    #     2. MODIFICATION: User wants to modify, adjust, or change something in the plan but does NOT include approval/proceed command in the same message
    #     3. APPROVED_EXTEND: User wants to modify something AND proceed/approve in the same message (e.g., "change article count to 50 then proceed", "update the timeline and go ahead", "make it 30 articles and continue", "adjust to 5 days then approve")
    
    #     Key distinction for APPROVED_EXTEND:
    #     - The message contains BOTH modification request AND approval/proceed command
    #     - Common patterns: "change X then proceed", "update X and continue", "make it X then go ahead", "adjust X and approve"
    
    #     Analyze the user message and classify it accurately."""
    
    #     user_prompt = f"""User Message: "{user_message}"
    
    #     Classify this message and provide your analysis in JSON format with the following structure:
    #         {{
    #             "classification": "approval|modification|approved_extend",
    #             "confidence": 0.0-1.0
    #         }}
    
    #     Important: Return ONLY a valid JSON object. No additional text."""
    
    #     raw_output = await base_llm.ainvoke(f"{system_prompt}\n\n{user_prompt}")
    #     try:
    #         result = json.loads(extract_json_from_llm_response(raw_output.content))
    #     except Exception as _:
    #         # Fallback logic for parsing errors
    #         content_lower = raw_output.content.lower()
    #         if "approved_extend" in content_lower:
    #             result = {
    #                 "classification": "approved_extend",
    #                 "confidence": 0.8
    #             }
    #         elif "approval" in content_lower:
    #             result = {
    #                 "classification": "approval",
    #                 "confidence": 1.0
    #             }
    #         else:
    #             result = {
    #                 "classification": "modification",
    #                 "confidence": 0.0
    #             }
    #     return result
    
    
    # async def planner_agent(state: State = {}) -> Dict[str, Any]:
    #         user_intent = state.get('user_intent',{})
    #         packs = state.get('research_packs',[])
    #         entity_name = user_intent.get('entity', 'CompanyName')
    #         geographies_list = user_intent.get('geographies', ['global'])
    #         sanitized_packs = json.dumps(trim_articles(packs)).replace("{", "{{").replace("}", "}}")
        
    #         sanitized_user_intent = json.dumps(user_intent).replace("{", "{{").replace("}", "}}")
    #         conversation_history = state.get('planner_agent_state',{}).get('conversation_history',[])
    #         auto_approve = False
        
    #         if state.get('planner_agent_state',{}).get('check_plan_approval',False):
    #             user_message = conversation_history[-1].get('content')
    #             research_plan = state.get('planner_agent_state',{}).get('research_plan',{})
    #             classification_result = await planner_classifier_agent(user_message)
    #             print("Classification result: ",classification_result)
            
    #             if classification_result.get('classification','').lower() == 'approval':
    #                 research_plan["user_approval_status"] = "approved"
    #                 state.update({
    #                 "user_interception_state": {
    #                 "requested": False,
    #                 "node": "end"
    #                 },
    #                 "planner_agent_state": {
    #                     "conversation_history": [],
    #                     "extra_data": {},
    #                     "check_plan_approval": False,
    #                     "research_plan": {}
    #                 },
    #                 "research_plan": research_plan
    #                 })
    #                 return state
    #             elif classification_result.get('classification','').lower() == 'approved_extend':
    #                 auto_approve = True
    #                 print("Auto-approve flag set: User requested modifications with approval")
    
    #         system = f"""You are the Planning and Delegation Lead who is currently planning for media monitoring research based on user intent.
    #     Your job is to convert the provided user intent into a structured plan for execution by Researcher Agents and Writer Agents.
    #     You can create multiple sections based on the user query and the entity/company if required.
    
    #     USER_INTENT:
    #     {     }
    
    #     CRITIAL: Today's date is {datetime.now().strftime('%Y-%m-%d')} (Format: YYYY-MM-DD). Always use this date as the reference date for the time_range creation.
    
    #     ### Agent Capabilities
    #     **RESEARCHER AGENT**:
    #     - Fetches and collects news articles from multiple sources (vector database, web search)
    #     - Extracts structured data: headlines, outlets, dates, URLs, authors, summaries
    #     - Identifies CXO mentions, competitor mentions, product mentions, financial data, market trends
    #     - Provides raw data collection without deep analysis
    #     - Best for: Data gathering, article collection, information retrieval
    #     - **LIMITATIONS**: Cannot generate images, graphics, charts, or visual content
    
    #     **WRITER AGENT**:
    #     - Analyzes and synthesizes existing research data
    #     - Creates reports, summaries, and insights from collected data
    #     - Performs comparative analysis, trend identification, narrative synthesis
    #     - Generates executive summaries, risk assessments, opportunity analysis
    #     - Best for: Analysis, synthesis, report generation, strategic insights
    #     - **LIMITATIONS**: Cannot generate images, graphics, charts, diagrams, or any visual content. Only produces text-based reports, summaries, and analysis.
    
    #     ### Rules
    #     - Do not overplan for simple queries.
    #     - Always scope-limit the plan to the user query.
    #     - Select only the sections relevant to the query.
    #     - You can decide on sections based on the user query like "company_news", "competitors", "risks_crisis", "policy", "cxo_mentions", "landscape", "outlets_journalists", "narrative", "social".
    #     - **CRITICAL**: For each section, determine if it requires "research" (data collection) or "analysis" (data synthesis):
    #     * Use "research" for sections that need NEW data collection from sources
    #     * Use "analysis" for sections that need synthesis/analysis of EXISTING research data
    #     - **CRITICAL - NO IMAGE GENERATION**:
    #     * Writer Agent and Researcher Agent CANNOT generate images, graphics, charts, diagrams, infographics, or any visual content
    #     * Do NOT include image generation, chart creation, or visual content generation in any plan
    #     * All deliverables must be text-based: reports, summaries, analysis, written insights
    #     * If user requests images/charts, plan text-based alternatives (descriptions, data tables, written analysis)
    #     - For research sections: Output actionable data collection tasks, not summaries or analysis.
    #     - For analysis sections: Output analytical objectives and synthesis goals.
    #     - Each task should specify: focus, methods, and steps to reach the goal.
    #     - Provide clear success criteria for this plan.
    #     - Facts must be backed by externally retrieved sources from this session; internal model knowledge is not allowed.
    #     - Each deliverable must specify explicit source requirements (URL/date/outlet/author/summary). "No source, no claim."
    #     - Tooling: Recommend ONLY tools that the Researcher Agent actually has access to: qdrant tools (Primary preindexed vector database tools, Always call it "Primary Tools") for vector database and google tools for web search (Secondary web search tools always call it "Secondary Tools").
    #     - All research sections must use both tool sets. Secondary Tools alone is not allowed.
    #     - Analysis sections do not need tool recommendations as they work with existing data.
    #     - Use existing research data packs to plan the research mode (extend|new_pack).
    #     - Currently the system supports news and article sources, so plan accordingly.
    #     - If geographies are not provided consider the global coverage and do not specify any specific geography.
    #     - Do not mention specific tool names in the plan. instead use "Primary Tools" and "Secondary Tools".
    #     - Avoid mentioning any specific formatting (like json, markdown, etc.) about the result in section plan.
    #     - If articles_target is specified in the user intent, use that as the baseline target. If not specified or null: based on the user intent and the existing research data packs plan the number of articles to be covered to get a better research result.
    
    #     ### Instructions
    #     1. Start by analyzing the user intent and then break it into meaningful chunks of independent plan sections.
    #     2. For each section, determine the section_type:
    #         - **"research"**: If the section requires NEW data collection (articles, news, sources)
    #         - **"analysis"**: If the section requires analysis/synthesis of research data
    #         - Example research sections: "Latest Company News", "Competitor Coverage", "CXO Mentions in Media"
    #         - Example analysis sections: "Sentiment Analysis Summary", "Competitive Landscape Analysis", "Risk Assessment Report", "Trend Identification"
    #     3. Make sure you have properly expanded and compiled scope for each section:
    #         - For research sections: Define clear "scope_of_research" with data collection objectives, what to look for, and what data points to extract
    #         - For analysis sections: Define detailed "scope_of_analysis" with specific analytical tasks, insights to generate, and synthesis objectives
    #     4. Make sure each section can be executed independently:
    #         - Research sections by Researcher Agent (data collection)
    #         - Analysis sections by Writer Agent (data synthesis)
    #     5. While planning the target counts for research sections, make sure to accommodate existing relevant research data packs so that the total target is met.
    #         - Example: if user want to analyze a total of 30 articles but existing pack has 10 relevant articles, then the target should be 20.
    #         - Example: if user want to add 10 more articles but existing pack has 20 articles, then the target should be 10 since existing relevant pack count is irrelevant here.
    #     6. For analysis sections, set articles_target to 0 as they work with existing data.
    #     7. For analysis sections, the scope_of_analysis MUST be comprehensive and actionable:
    #         - Specify exact analytical questions to answer
    #         - Define key insights and patterns to identify
    #         - List specific metrics or dimensions to analyze (sentiment, trends, impact, etc.)
    #         - Describe synthesis goals and how to structure the output
    #         - Include context about what the analysis should reveal
    #     8. Use custom format if user intent does not specify report.
    #     When you choose `custom` format consider the following:
    #         - detailed description of how the research results should be formatted when research is completed to the user.
    #         - Identify a suitable user readable content formatting if expected format type is custom.
    #     Choose `report` format :
    #         - if the user's query (in the "query" field of user_intent) contains any of these keywords: "media monitoring report", "coverage report", "monitoring report", "media report"
    
        
    #     ### Existing Research Data Packs
    #     {sanitized_packs}
    # """
    #         human = f"""
    #     ### Output JSON Schema
    #     {{format_instructions}}
    #     Important: Return ONLY a JSON object following this exact schema. No additional text.
    
    #     User Input:
    #     {{input}}
    # """
    
    #         format_instructions = f"""
    #     ```json
    #     {{
    #         "time_range": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}},
    #         "report_format": "custom|report",
    #         "custom_report_format": "description of the custom report formatting for research results when research is completed, add the formating information for the research results, do not add statements like when research is completed, or after research is completed, etc.",
    #         "user_approval_status": "pending",
    #         "user_confirmation_message": "a message to be shown to user asking for confirmation",
    #         "sections": [
    #             {{
    #                 "id": "{entity_name}_<section_id>",
    #                 "section_type": "research|analysis",
    #                 "time_range": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}},
    #                 "title": "title of the section",
    #                 "plan": "markdown concise high level plan for the section which is understandable by a non technical user",
    #                 "entity": "{entity_name}",
    #                 "research": {{"mode": "extend|new_pack","extend_pack_id": "..."}},
    #                 "scope_of_research": "identify all news articles mentioning [entity] in relation to product launches, extract headlines, summaries, dates, outlets, CXO quotes, and competitor mentions (for research sections)",
    #                 "scope_of_analysis": "analyze sentiment trends across collected articles, identify key themes in media coverage, assess competitive positioning based on media mentions, evaluate crisis indicators, and synthesize strategic implications for stakeholders (for analysis sections)",
    #                 "coverage_type": "company_news|competitors|risks_crisis|policy|cxo_mentions|landscape|narrative|analysis",
    #                 "coverage_scope": "global",
    #                 "competitors": [],
    #                 "tone": "neutral|executive|technical",
    #                 "audience": "CXO|PR|analyst",
    #                 "length": "brief|standard|deep-dive",
    #                 "geographies": {geographies_list},
    #                 "languages": ["en"],
    #                 "articles_target":  < number of articles required based on user intent and existing research data packs>,
    #                 "retries": 0,
    #                 "section_verifier_report": null,
    #                 "failed_research_pack": null
    #             }}
    #         ]
    #     }}
    #     ```
    
    #     **SECTION_TYPE FIELD EXPLANATION**:
    #     - "research": Section requires Researcher Agent to collect NEW data from sources (articles, news, etc.)
    #     * For research sections, populate "scope_of_research" with detailed data collection objectives
    #     * Leave "scope_of_analysis" as empty string or null for research sections
    #     - "analysis": Section requires Writer Agent to analyze/synthesize research data
    #     * For analysis sections, populate "scope_of_analysis" with comprehensive analytical instructions
    #     * Leave "scope_of_research" as empty string or null for analysis sections
    
    #     **SCOPE FIELD GUIDELINES**:
    #     - scope_of_research (for research sections): What data to find, where to look, what to extract
    #     - scope_of_analysis (for analysis sections): What to analyze, what insights to generate, what patterns to identify, how to synthesize findings
    #     """
    
    #         prompt = ChatPromptTemplate.from_messages(
    #             [("system", system),
    #             MessagesPlaceholder("chat_history", optional=True),
    #             ("human", human),MessagesPlaceholder("agent_scratchpad")]
    #             ).partial(format_instructions=format_instructions)
            
    #         tools: list = []  # add tools if/when you have them
    #         agent = create_tool_calling_agent(
    #             llm=base_reasoning_llm,
    #             tools=tools,
    #             prompt=prompt,
    #         )
    
    #         chat_history = [(HumanMessage(content=chat.get('content')) if chat.get('role') == 'user' else AIMessage(content=chat.get('content'))) for chat in conversation_history]
    #         executor = AgentExecutor(
    #             agent=agent,
    #             tools=[],
    #             verbose=True,
    #             handle_parsing_errors=True,
    #             early_stopping_method="generate",
    
    #         )
    
        
    #         if conversation_history:
    #             input_message = conversation_history[-1]['content']
    #         else:
    #             input_message = "Please plan the research for the user intent."
            
    #         retry = 0
    #         while retry < 3:
    #             raw_output = await executor.ainvoke({
    #                 "input": input_message,
    #                 "chat_history": chat_history,
    #             })
    #             if DEBUG_MODE:
    #                 print(f"PLANNER AGENT - raw_output: {raw_output.get('output')}")
    #             try:
    #                 result = json.loads(extract_json_from_llm_response(raw_output.get("output")))
    #                 if not isinstance(result, dict):
    #                     raise Exception(f"output is invalid. Please try again.")
    #                 break
    #             except Exception as e:
    #                 print(f"PLANNER AGENT - error: {e}")
    #                 retry += 1
    #                 input_message = f"output is invalid. Please try again."
    #                 if retry == 3:
    #                     raise Exception(f"output is invalid. Please try again.")
    #                 continue
    #         chat_history = chat_history + [HumanMessage(content=input_message),AIMessage(content=json.dumps(result, indent=2).replace("{", "{{").replace("}", "}}"))]
    #         messages = conversation_history + [{"role": "planner", "content": json.dumps(result, indent=2).replace("{", "{{").replace("}", "}}")}]
    #         section_plans = [{"title": section.get("title"),"plan": section.get("plan")} for section in result.get("sections",[])]
    #         user_approval_message = result.get("user_confirmation_message")
    #         report_format_message = "Upon completion generate a standard media monitoring report."
    #         if result.get("report_format") == "custom":
    #             report_format_message = result.get("custom_report_format")
    
    #         # Check if we should auto-approve (for approved_extend classification)
    #         if auto_approve:
    #             result["user_approval_status"] = "approved"
    #             state.update({
    #                 "user_interception_state": {
    #                     "requested": False,
    #                     "node": "end"
    #                 },
    #                 "planner_agent_state": {
    #                     "conversation_history": [],
    #                     "extra_data": {},
    #                     "check_plan_approval": False,
    #                     "research_plan": {}
    #                 },
    #                 "research_plan": result
    #             })
    #             return state
    #         raw_out = await base_llm.ainvoke(f"Analyze the json/message plan details given, your goal is to properly format the following plan details in a user readable markdown format. always display the time range in the message: \n Message: {json.dumps(section_plans).replace("{", "{{").replace("}", "}}")}\n\n ##Message to user\n {user_approval_message} \n\n\n Important: Return ONLY a markdown message(don't include markdown tags like ```markdown ``` in the message). No additional text.")
    #         user_message_formatted = raw_out.content
    #         user_message_formatted = f"{user_message_formatted}\n\n Result Format:\n {report_format_message}"
    #         state.update({
    #         "messages": state.get('messages',[]) + [AIMessage(content=user_message_formatted)],
    #         "user_interception_state": {
    #             "requested": True,
    #             "node": "planner_agent"
    #             },
    #         "planner_agent_state": {
    #             "check_plan_approval": True,
    #             "conversation_history": messages,
    #             "extra_data": state.get('planner_agent_state',{}).get('extra_data',{}),
    #             "research_plan": result
    #             }
    #         })
    #         return state