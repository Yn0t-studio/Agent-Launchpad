import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
import urllib.request
from agent import get_agent

# Patch engineio to allow more packets (fixes 'Too many packets in payload' error)
try:
    from engineio.payload import Payload
    Payload.max_decode_packets = 500
except ImportError:
    pass

try:
    from telemetry import get_langfuse_callback
except ImportError:
    def get_langfuse_callback():
        return None

def check_ollama_connection():
    try:
        urllib.request.urlopen("http://localhost:11434")
        return True
    except Exception:
        return False

@cl.on_chat_start
async def on_chat_start():
    if not check_ollama_connection():
        await cl.Message(content="⚠️ **Warning:** Could not connect to Ollama. Please ensure it is running at http://localhost:11434").send()
        return

    agent = get_agent()
    cl.user_session.set("agent", agent)
    cl.user_session.set("history", [])
    cl.user_session.set("telemetry_handler", get_langfuse_callback())

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    history = cl.user_session.get("history")
    
    if agent is None:
        await cl.Message(content="Ollama is not connected. Please restart the app after starting Ollama.").send()
        return

    # Create the main answer message
    final_answer = cl.Message(content="")
    
    # Create the thinking step
    thinking_step = cl.Step(name="Thinking Process", type="process")
    
    # Prepare input for the agent (LangGraph state)
    # The state schema expects 'messages'
    # We append the user message to the history
    input_messages = history + [HumanMessage(content=message.content)]
    
    # Prepare config with telemetry if available
    config = {"callbacks": [cl.user_session.get("telemetry_handler")] if cl.user_session.get("telemetry_handler") else []}
    
    # Start the thinking step
    await thinking_step.stream_token("Thinking...\n") 

    # Use astream_events to capture tokens and route them
    async for event in agent.astream_events({"messages": input_messages}, config=config, version="v2"):
        kind = event["event"]
        
        # Check if the event matches the stream output from a chat model
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Check which node produced this event
                # LangGraph adds metadata including 'langgraph_node'
                node_name = event.get("metadata", {}).get("langgraph_node")
                
                if node_name == "reasoner":
                    await thinking_step.stream_token(content)
                elif node_name == "responder":
                    await final_answer.stream_token(content)
    
    # Send the final results
    await thinking_step.send()
    await final_answer.send()
    
    # Update history with the user message and the final answer
    # We consciously do not add the reasoning trace to the history to keep it clean,
    # or we could if we wanted the agent to remember its reasoning.
    # For now, let's keep it simple: User Message -> Final Answer.
    history.append(HumanMessage(content=message.content))
    history.append(AIMessage(content=final_answer.content))
    cl.user_session.set("history", history)
