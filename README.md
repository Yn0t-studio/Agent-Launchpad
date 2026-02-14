# AI Persona

A local AI chat interface built with [Chainlit](https://github.com/Chainlit/chainlit), [LangChain](https://github.com/langchain-ai/langchain), [Ollama](https://ollama.com/), and [Deep Agents](https://github.com/deep-agents/deep-agents).

## Features

- 💬 **Interactive Chat**: Clean, modern chat interface provided by Chainlit.
- 🤖 **Deep Agent**: Powered by `deepagents` for advanced agentic capabilities.
- 🔒 **Local Privacy**: Runs entirely locally using Ollama and Llama 3.1.
- 📝 **Context Aware**: Maintains conversation history.
- ⚡ **Streaming**: Real-time token streaming.

## Prerequisites

1.  **Python 3.10 or higher**
2.  **[Ollama](https://ollama.com/)** running locally.

### Setup Ollama

Install Ollama and pull the Llama 3.1 model:

```bash
ollama pull llama3.1
```

Start the Ollama server:

```bash
ollama serve
```

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Yn0t-studio/AI-Persona.git
    cd AI-Persona
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Ensure Ollama is running (`ollama serve`).

2.  Run the application:
    ```bash
    chainlit run app.py -w
    ```

3.  Open `http://localhost:8000` to chat.

## Configuration

### Changing the Model or Tools

Edit `agent.py` to configure the agent:

```python
def get_agent():
    # ...
    model = ChatOllama(model="llama3.1", base_url="http://localhost:11434")
    
    # Add tools or customize the agent here
    agent = create_deep_agent(model=model, tools=[])
    
    return agent
```
