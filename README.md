# Agent Launchpad Template

🚀 **Get up and running with a local conversational agent in minutes.**

This project is a minimal, deep-agentic template designed for experimenting with local LLMs. It combines **[Chainlit](https://github.com/Chainlit/chainlit)** for the chat interface, **[Ollama](https://ollama.com/)** for local model inference, and **[Deep Agents](https://github.com/deep-agents/deep-agents)** for agentic capabilities.

Use this as a starting point to build your own custom AI personas and agents.

## Features

- ⚡ **Instant Setup**: Clone, install, and chat.
- 🏗️ **Template Structure**: Clean, modular code ready for customization.
- 💬 **Interactive UI**: Polished chat interface out-of-the-box.
- � **Agentic Core**: Powered by `deepagents` (based on LangGraph).
- 🔒 **100% Local**: Privacy-first using Llama 3.1 via Ollama.

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
    git clone https://github.com/Yn0t-studio/Agent-Launchpad.git
    cd Agent-Launchpad
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
