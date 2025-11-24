import json 
from app.core.state import State
from app.agents.base_agent import llm_model

def writer_agent(state: State = {}):
    """
    Writer agent that generates a comprehensive report from research data.
    
    Args:
        state: State object containing research_data
        
    Returns:
        Updated state with generated report
    """
    data = state.get('research_data', [])
    
    if not data:
        return {
            **state,
            'report': "No research data available to generate a report."
        }
    
    # Prepare article summaries for the LLM
    articles_summary = []
    for idx, article in enumerate(data, 1):
        articles_summary.append(
            f"{idx}. Title: {article.get('title', 'N/A')}\n"
            f"   URL: {article.get('url', 'N/A')}\n"
            f"   Description: {article.get('description', 'N/A')}"
        )
    
    articles_text = "\n\n".join(articles_summary)
    
    # Generate introductory paragraph using LLM
    intro_prompt = f"""You are a professional media analyst writing a report based on research data.

Based on the following articles, write a compelling introductory paragraph (2-3 sentences) that:
1. Summarizes the key themes and topics covered
2. Sets the context for the detailed articles that follow
3. Is professional and engaging

Articles:
{articles_text}

Write ONLY the introductory paragraph, no additional text or formatting."""

    try:
        intro_response = llm_model.invoke(intro_prompt)
        intro_paragraph = intro_response.content.strip()
    except Exception as e:
        print(f"Error generating introduction: {e}")
        intro_paragraph = "The following research data has been compiled from various sources."
    
    # Format the complete report
    report = f"{intro_paragraph}\n\n"
    report += "=" * 70 + "\n"
    report += "RESEARCH FINDINGS\n"
    report += "=" * 70 + "\n\n"
    
    for idx, article in enumerate(data, 1):
        report += f"Article {idx}\n"
        report += "-" * 70 + "\n"
        report += f"Title: {article.get('title', 'No Title Available')}\n\n"
        report += f"Description:\n{article.get('description', 'No description available.')}\n\n"
        report += f"URL: {article.get('url', 'N/A')}\n"
        report += "=" * 70 + "\n\n"
    print("=== REPORT AGENT OUTPUT ===")
    print(report)
    # Update state with the generated report
    return {
        **state,
        'report': report
    }
