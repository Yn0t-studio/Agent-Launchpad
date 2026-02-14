from langchain_ollama import ChatOllama
from deepagents import create_deep_agent

def get_agent():
    """
    Creates and returns a Deep Agent configured with Ollama (Llama 3).
    """
    model = ChatOllama(model="llama3.1", base_url="http://localhost:11434")
    
    # Create the Deep Agent
    # Tools are optional. We start without extra tools as requested.
    # The agent uses LangGraph under the hood.
    agent = create_deep_agent(model=model, tools=[])
    
    return agent
