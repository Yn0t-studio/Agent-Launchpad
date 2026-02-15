import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from agent import get_agent
from telemetry import get_langfuse_callback

# Define which nodes should emit to the main chat bubble.
# usually just the final node, but could be a set if you have multiple exit points.
FINAL_ANSWER_NODES = {"responder"} 

@cl.on_chat_start
async def on_chat_start():
    agent = get_agent()
    cl.user_session.set("agent", agent)

    # Initialize telemetry
    langfuse_handler = get_langfuse_callback()
    if langfuse_handler:
        cl.user_session.set("langfuse_handler", langfuse_handler)

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    history = cl.user_session.get("history") or []
    
    # Input for the graph
    input_messages = history + [HumanMessage(content=message.content)]
    
    # Retrieve the telemetry handler if it exists
    langfuse_handler = cl.user_session.get("langfuse_handler")
    
    # Create the config for the run
    run_config = {}
    if langfuse_handler:
        run_config["callbacks"] = [langfuse_handler]

    # 1. ALWAYS send the Thinking Step first to reserve the top slot
    thinking_step = cl.Step(name="Thinking Process")
    await thinking_step.send()

    # 2. DELAY creating the final message object
    final_answer = None 

    # 3. Dynamic Event Loop
    async for event in agent.astream_events(
        {"messages": input_messages}, 
        config=run_config,
        version="v2"
    ):
        kind = event["event"]
        
        # We only care about stream events from the Chat Model
        if kind == "on_chat_model_stream":
            
            # Get metadata to know which node is speaking
            node_name = event.get("metadata", {}).get("langgraph_node", "unknown")
            content = event["data"]["chunk"].content
            
            # Skip empty content (keep-alives)
            if not content:
                continue

            # Route content based on the node
            if node_name == "reasoner":
                # Stream to the thinking step
                await thinking_step.stream_token(content)
                
            elif node_name == "responder":
                # This is the final answer
                if final_answer is None:
                    # Close the thinking step before starting the answer
                    await thinking_step.update()
                    final_answer = cl.Message(content="")
                    await final_answer.send()
                
                await final_answer.stream_token(content)

    # 4. Cleanup
    # Close the thinking step if it hasn't been closed (e.g. if no answer was generated)
    await thinking_step.update()
    
    # Send/Update final answer
    if final_answer:
        await final_answer.update() # Ensure the message is marked as done
        # Update History
        history.append(HumanMessage(content=message.content))
        history.append(AIMessage(content=final_answer.content))
        cl.user_session.set("history", history)
    else:
        # Fallback if something went wrong and no answer was generated
        await cl.Message(content="Error: No response generated.").send()