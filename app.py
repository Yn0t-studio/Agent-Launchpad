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

    msg = cl.Message(content="")
    
    # Prepare input for the agent (LangGraph state)
    # The state schema likely expects 'messages'
    input_messages = history + [HumanMessage(content=message.content)]
    
    # Prepare config with telemetry if available
    # Create the config with the callback
    # If handler is None, LangChain simply ignores it.
    config = {"callbacks": [cl.user_session.get("telemetry_handler")] if cl.user_session.get("telemetry_handler") else []}
    
    # Log config
    print("Config:", config)    

    # Use astream_events to capture tokens from the model
    async for event in agent.astream_events({"messages": input_messages}, config=config, version="v2"):
        kind = event["event"]
        
        # Stream tokens from the chat model
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                await msg.stream_token(content)
    
    await msg.send()
    
    # Update history
    history.append(HumanMessage(content=message.content))
    history.append(AIMessage(content=msg.content))
    cl.user_session.set("history", history)
