import chainlit as cl
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
import urllib.request

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

    model = ChatOllama(model="llama3", base_url="http://localhost:11434")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )
    
    runnable = prompt | model | StrOutputParser()
    
    cl.user_session.set("runnable", runnable)
    cl.user_session.set("history", [])

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")
    history = cl.user_session.get("history")
    
    if runnable is None:
        await cl.Message(content="Ollama is not connected. Please restart the app after starting Ollama.").send()
        return

    msg = cl.Message(content="")
    
    async for chunk in runnable.astream(
        {"question": message.content, "history": history},
    ):
        await msg.stream_token(chunk)
    
    await msg.send()
    
    history.append(HumanMessage(content=message.content))
    history.append(AIMessage(content=msg.content))
    cl.user_session.set("history", history)
