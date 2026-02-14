import asyncio
from langchain_core.messages import HumanMessage
from agent import get_agent

async def main():
    print("Initializing agent...")
    try:
        agent = get_agent()
        print("Agent initialized.")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return

    print("Running agent with query 'Hello'...")
    input_messages = [HumanMessage(content="Hello")]
    
    try:
        async for event in agent.astream_events({"messages": input_messages}, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    print(content, end="", flush=True)
        print("\n\nAgent execution completed.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nError during execution: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(main())
