import sys
import os
import json
from unittest.mock import MagicMock

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Mock dependencies
sys.modules["langchain_tavily"] = MagicMock()
sys.modules["langchain_groq"] = MagicMock()
sys.modules["app.agents.base_agent"] = MagicMock()

# Mock TavilySearch
mock_tavily_instance = MagicMock()
sys.modules["langchain_tavily"].TavilySearch.return_value = mock_tavily_instance

# Mock LLM
mock_llm = MagicMock()
sys.modules["app.agents.base_agent"].llm_model = mock_llm

from app.agents.research_agent import research_agent

def test_research_agent():
    print("Starting Researcher Agent Verification (Mocked)...\n")
    
    # Setup Mock Data
    mock_tavily_instance.invoke.return_value = [{"url": "http://test.com", "content": "Test content"}]
    
    mock_extracted_data = {
        "articles": [
            {
                "headline": "Test Article",
                "summary": "This is a test summary",
                "publication_date": "2025-11-24",
                "source": "Test Source",
                "url": "http://test.com",
                "quotes": ["Test quote"]
            }
        ]
    }
    
    mock_response = MagicMock()
    mock_response.content = json.dumps(mock_extracted_data)
    mock_llm.invoke.return_value = mock_response

    # Test Case 1: Mixed sections (Research + Analysis)
    print("=" * 60)
    print("Test 1: Mixed Sections (Research + Analysis)")
    print("=" * 60)
    
    state = {
        "intent": "Research company X",
        "sections": [
            {
                "title": "Company X News",
                "section_type": "research",
                "scope_of_research": "Find news about Company X"
            },
            {
                "title": "Sentiment Analysis",
                "section_type": "analysis",
                "scope_of_analysis": "Analyze sentiment"
            }
        ]
    }
    
    try:
        result = research_agent(state)
        research_data = result.get("research_data", [])
        
        print(f"[PASS] Agent execution completed")
        print(f"  Research items count: {len(research_data)}")
        
        if len(research_data) == 1:
            print(f"[PASS] Correctly filtered for 1 research section")
        else:
            print(f"[FAIL] Expected 1 research item, got {len(research_data)}")
            
        if research_data and research_data[0]["section_title"] == "Company X News":
            print(f"[PASS] Correct section processed")
        else:
            print(f"[FAIL] Wrong section processed")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

    # Test Case 2: No Research Sections
    print("\n" + "=" * 60)
    print("Test 2: No Research Sections")
    print("=" * 60)
    
    state_no_research = {
        "intent": "Analyze only",
        "sections": [
            {
                "title": "Analysis Only",
                "section_type": "analysis"
            }
        ]
    }
    
    try:
        result = research_agent(state_no_research)
        research_data = result.get("research_data", [])
        
        if not research_data:
            print(f"[PASS] Correctly skipped execution (no research data)")
        else:
            print(f"[FAIL] Should not have produced research data")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test Case 3: Serialization Error Handling
    print("\n" + "=" * 60)
    print("Test 3: Serialization Error Handling")
    print("=" * 60)
    
    # Simulate a search result containing a non-serializable object (like an Exception)
    mock_tavily_instance.invoke.return_value = [{"error": ValueError("Some error")}]
    
    state_serialization = {
        "intent": "Test serialization",
        "sections": [
            {
                "title": "Serialization Test",
                "section_type": "research",
                "scope_of_research": "Test query"
            }
        ]
    }
    
    try:
        result = research_agent(state_serialization)
        research_data = result.get("research_data", [])
        
        if research_data and research_data[0].get("articles") is not None:
             print(f"[PASS] Successfully handled non-serializable object")
        else:
             print(f"[FAIL] Failed to handle non-serializable object")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test Case 5: API Error Handling (e.g., Query too long)
    print("\n" + "=" * 60)
    print("Test 5: API Error Handling")
    print("=" * 60)
    
    # Simulate Tavily returning an error dict
    mock_tavily_instance.invoke.return_value = {"error": "Error 400: Query is too long."}
    
    state_api_error = {
        "intent": "Test API Error",
        "sections": [
            {
                "title": "API Error Test",
                "section_type": "research",
                "scope_of_research": "Some query"
            }
        ]
    }
    
    try:
        result = research_agent(state_api_error)
        research_data = result.get("research_data", [])
        
        if research_data and research_data[0].get("error") == "Error 400: Query is too long.":
             print(f"[PASS] Successfully handled API error. Error: {research_data[0]['error']}")
             if not research_data[0]["articles"]:
                 print(f"[PASS] Articles list is empty as expected")
        else:
             print(f"[FAIL] Failed to handle API error correctly")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    print("\n" + "=" * 60)
    print("Verification Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_research_agent()
