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
    
    # 1. State Tracking
    final_answer = None   # The main message bubble
    current_step = None   # The current intermediate step
    cur_node = None       # Track which node we are currently processing

    # Input for the graph
    input_messages = history + [HumanMessage(content=message.content)]
    
    # Retrieve the telemetry handler if it exists
    langfuse_handler = cl.user_session.get("langfuse_handler")
    
    # Create the config for the run
    run_config = {}
    if langfuse_handler:
        run_config["callbacks"] = [langfuse_handler]

    # 2. Dynamic Event Loop
    async for event in agent.astream_events(
        {"messages": input_messages}, 
        config=run_config,
        version="v2"
    ):
        kind = event["event"]
        
        # We only care about stream events from the Chat Model
        if kind == "on_chat_model_stream":
            
            # Get metadata to know which node is speaking
            # Fallback to "unknown" if metadata is missing
            new_node = event.get("metadata", {}).get("langgraph_node", "unknown")
            content = event["data"]["chunk"].content
            
            # Skip empty content (keep-alives)
            if not content:
                continue

            # --- NODE TRANSITION LOGIC ---
            # If the node has changed, we need to handle the UI transition
            if new_node != cur_node:
                
                # Close the previous step if it exists
                if current_step:
                    await current_step.update()
                    current_step = None
                
                cur_node = new_node
                
                # Check: Is this new node a "Final Answer" node?
                if new_node in FINAL_ANSWER_NODES:
                    # We are now in the final phase.
                    # Create the final answer message if it doesn't exist yet.
                    if not final_answer:
                        final_answer = cl.Message(content="")
                else:
                    # It's an intermediate node. Create a new Step for it.
                    # The name of the step becomes the name of the node (e.g., "web_search")
                    # You can format this string to look nicer (e.g. .replace("_", " ").title())
                    step_name = new_node.replace("_", " ").title()
                    current_step = cl.Step(name=step_name, type="process")
                    await current_step.send()

            # --- STREAMING LOGIC ---
            # Route the content to the correct place
            if current_step:
                await current_step.stream_token(content)
            elif final_answer:
                await final_answer.stream_token(content)

    # 3. Cleanup
    # Close any dangling steps
    if current_step:
        await current_step.update()
    
    # Send final answer
    if final_answer:
        await final_answer.send()
        # Update History
        history.append(HumanMessage(content=message.content))
        history.append(AIMessage(content=final_answer.content))
        cl.user_session.set("history", history)
    else:
        # Fallback if something went wrong and no answer was generated
        await cl.Message(content="Error: No response generated.").send()