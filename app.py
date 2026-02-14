import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
import urllib.request
from agent import get_agent

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
    
    # Use astream_events to capture tokens from the model
    async for event in agent.astream_events({"messages": input_messages}, version="v2"):
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
