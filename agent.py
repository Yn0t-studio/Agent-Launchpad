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
Do NOT provide the final answer yet. Focus on breaking down the problem, identifying key information, and planning the response.
Start your response with "Thinking Process:" or similar.""")
        
        # We invoke the model with the system prompt + conversation history
        # We might want to wrap this in a way that distinguishing it as "thought"
        # For now, we'll just append it. Check app.py for how this is routed.
        response = await model.ainvoke([system_prompt] + messages)
        
        # We return a message that identifies itself as coming from the reasoner?
        # LangGraph adds the result to the state.
        # We can add a custom property or just rely on the node name for routing in stream_events.
        return {"messages": [response]}

    # Define the Responder Node
    async def responder(state: AgentState):
        """
        Generates the final answer based on the original query and the reasoner's output.
        """
        messages = state["messages"]
        
        # System prompt for the final response
        system_prompt = SystemMessage(content="""You are the Final Responder.
Review the user's request and the Reasoning Engine's analysis (the latest message).
Provide a clear, concise, and helpful final answer to the user.
Do not repeat the "Thinking Process" explicitly, just use it to inform your answer.""")
        
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
