import os
from langfuse.langchain import CallbackHandler

def get_langfuse_callback():
    """
    Returns a Langfuse callback handler if keys are present.
    Otherwise returns None.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if public_key and secret_key:
        return CallbackHandler(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
    
    print("⚠️ Langfuse keys not found. Tracing is disabled.")
    return None