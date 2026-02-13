# AI Persona

A simple, local AI chat interface built with [Chainlit](https://github.com/Chainlit/chainlit), [LangChain](https://github.com/langchain-ai/langchain), and [Ollama](https://ollama.com/).

## Features

- 💬 **Interactive Chat**: Clean, modern chat interface provided by Chainlit.
- 🔒 **Local Privacy**: Runs entirely locally using Ollama and Llama 3.
- 📝 **Context Aware**: Maintains conversation history for context-aware responses.
- ⚡ **Streaming**: Real-time token streaming for faster response perception.

## Prerequisites

Before running the application, ensure you have the following installed:

1.  **Python 3.10 or higher**
2.  **[Ollama](https://ollama.com/)** running locally.

### Setup Ollama

Install Ollama and pull the Llama 3 model (or your preferred model):

```bash
ollama pull llama3
```

Make sure the Ollama server is running:

```bash
ollama serve
```

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Yn0t-studio/AI-Persona.git
    cd AI-Persona
    ```

2.  Create and activate a virtual environment (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Ensure Ollama is running in a separate terminal:
    ```bash
    ollama serve
    ```

2.  Run the Chainlit application:
    ```bash
    chainlit run app.py -w
    ```
    *(The `-w` flag enables auto-reloading during development)*

3.  Open your browser to `http://localhost:8000` to start chatting!

## Configuration

To change the model, edit `app.py` and modify the `ChatOllama` initialization:

```python
model = ChatOllama(model="llama3", base_url="http://localhost:11434")
```
