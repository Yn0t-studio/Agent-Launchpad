import asyncio
from langchain_core.messages import HumanMessage
from agent import get_agent

async def test_agent():
    print("--- Starting Agent Test (Content Debug) ---")
    
    # 1. Initialize Agent
    try:
        agent = get_agent()
        print("✅ Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    # 2. Prepare Input
    input_messages = [HumanMessage(content="What is 2 + 2?")]
    
    # 3. Stream Events
    print("\n--- Streaming Events ---")
    reasoner_seen = False
    responder_seen = False
    
    try:
        async for event in agent.astream_events({"messages": input_messages}, version="v2"):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = chunk.content
                metadata = event.get("metadata", {})
                node_name = metadata.get("langgraph_node")
                
                # Debug print for every chunk
                # print(f"Node: {node_name}, Content: {repr(content)}")
                
                if content:
                    if node_name == "reasoner":
                        if not reasoner_seen:
                            print("\n[Reasoner Node Output Started]")
                            reasoner_seen = True
                        print(content, end="", flush=True)
                        
                    elif node_name == "responder":
                        if not responder_seen:
                            print("\n\n[Responder Node Output Started]")
                            responder_seen = True
                        print(content, end="", flush=True)
    except Exception as e:
         print(f"\n❌ Error during streaming: {e}")
         return

    print("\n\n--- Test Results ---")
    if reasoner_seen:
        print("✅ Reasoner node executed")
    else:
        print("❌ Reasoner node DID NOT execute")
        
    if responder_seen:
        print("✅ Responder node executed")
    else:
        print("❌ Responder node DID NOT execute")

if __name__ == "__main__":
    asyncio.run(test_agent())
