from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END, add_messages

# Define the state of the agent
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def get_agent():
    """
    Creates and returns a LangGraph agent configured with Ollama (Llama 3).
    The agent has two nodes: 'reasoner' and 'responder'.
    """
    model = ChatOllama(model="llama3.1", base_url="http://localhost:11434")

    # Define the Reasoner Node
    async def reasoner(state: AgentState):
        """
        Generates a step-by-step thinking process/plan.
        """
        messages = state["messages"]
        
        # System prompt to encourage thinking/planning
        system_prompt = SystemMessage(content="""You are the Reasoning Engine. 
Your goal is to analyze the user's request and outline a step-by-step plan or thinking process to solve it.
Even for simple greetings like "Hello", you must plan your response (e.g., "1. Acknowledge user. 2. Ask how to help.").
Do NOT provide the final answer to the user in this step. ONLY provide the internal reasoning/plan.
Start your response with "Thinking Process:".""")
        
        # We invoke the model with the system prompt + conversation history
        response = await model.ainvoke([system_prompt] + messages)
        
        # We return a message that identifies itself as coming from the reasoner
        return {"messages": [response]}

    # Define the Responder Node
    async def responder(state: AgentState):
        """
        Generates the final answer based on the original query and the reasoner's output.
        """
        messages = state["messages"]
        
        # System prompt for the final response
        system_prompt = SystemMessage(content="""You are the Final Responder.
Your job is to generate the final response to the user.
You will be provided with the user's request and the Reasoning Engine's analysis (the latest message).
Use the Reasoning Engine's plan to craft your response.
You MUST provide a response to the user. Do not be silent.
Do not repeat the "Thinking Process" explicitly. just answer the user directly.""")
        
        response = await model.ainvoke([system_prompt] + messages)
        return {"messages": [response]}

    # Build the Graph
    workflow = StateGraph(AgentState)

    workflow.add_node("reasoner", reasoner)
    workflow.add_node("responder", responder)

    workflow.set_entry_point("reasoner")
    workflow.add_edge("reasoner", "responder")
    workflow.add_edge("responder", END)

    return workflow.compile()
