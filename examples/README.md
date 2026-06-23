# Stage 0 Examples

This directory contains executable example solutions for each exercise in Stage 0: "The API Foundation". These examples demonstrate core concepts of interacting with OpenAI-compatible API endpoints and can be used to verify your understanding or as reference implementations.

## Quick Start

```bash
# 1. Run the setup script from the project root
bash scripts/setup.sh

# 2. Activate the virtual environment (optional but recommended)
source .venv/bin/activate

# 3. Run an example
python3 examples/stage0/exercise_1.py
```

## Exercise Overview

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Make Your First API Call - Basic request/response cycle |
| `exercise_2.py` | 2 | Experiment with Temperature - How temperature affects creativity |
| `exercise_3.py` | 3 | System Prompt Power - How system prompts change response style |
| `exercise_4.py` | 4 | Multi-Turn Conversation - Maintaining conversation history |
| `exercise_5.py` | 5 | Max Tokens Limitation - What happens when you hit token limits |
| `exercise_6.py` | 6 | Error Handling - How the API responds to invalid requests |
| `exercise_7.py` | 7 | Token Cost Calculation - Understanding API usage costs |

## Running Individual Examples

All examples must be run from the **project root directory** (not from within `examples/`):

```bash
# Run a single example
python3 examples/stage0/exercise_1.py

# Run all examples sequentially
for i in {1..7}; do python3 examples/stage0/exercise_$i.py; done
```

## Requirements

### Python Dependencies

```bash
pip install -r requirements.txt
```

The project requires:
- `python-dotenv` - For loading environment variables from `.env`
- Standard library only for HTTP (`urllib`) - no `requests` dependency needed

### API Server

The examples require a running OpenAI-compatible API server. By default, they are configured for **Ollama** running locally:

```bash
# Start Ollama
ollama serve

# Pull a model if you don't have one
ollama pull llama3
```

## Configuration

Create a `.env` file in the project root (or copy from `.env.example`):

```bash
API_BASE=http://localhost:8080
MODEL=llama3
API_KEY=ollama
```

### Supported API Endpoints

| Provider | API_BASE | API_KEY | Example Model |
|----------|----------|---------|---------------|
| Local (this device) | `http://localhost:8080` | `ollama` | `llama3`, `mistral` |
| Ollama | `http://localhost:11434` | `ollama` | `llama3`, `mistral` |
| vLLM | `http://localhost:8000` | (optional) | Depends on deployment |
| Groq | `https://api.groq.com/openai` | Your API key | `llama3-70b-8192` |
| OpenAI | `https://api.openai.com/v1` | Your API key | `gpt-3.5-turbo` |

## Troubleshooting

### `ModuleNotFoundError: No module named 'utils'`
Make sure you're running examples from the project root, not from the `examples/` directory.

### `ModuleNotFoundError: No module named 'dotenv'`
Install dependencies: `pip install -r requirements.txt`

### `URL Error: [Errno 61] Connection refused`
Your API server is not running. Start Ollama with `ollama serve`.

### `HTTP Error 404`
The model specified in `.env` may not be available. Pull it with `ollama pull <model_name>`.