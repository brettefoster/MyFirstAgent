# Stage Examples

This directory contains executable example solutions for each exercise across all stages. Each stage's examples demonstrate the core concepts of that stage's topic and can be used to verify your understanding or as reference implementations.

---

## Stage Overview

| Stage | Topic |
|-------|-------|
| Stage 0 | The API Foundation - Basic API requests and responses |
| Stage 1 | Raw Sensor - Streaming from the API |
| Stage 2 | Thinking Observer - Observing thinking patterns |
| Stage 3 | State Engine - Conversation state management |
| Stage 4 | Parsing Bridge - Real-time tool call parsing |
| Stage 5 | Sandboxed Hand - Tool registration and execution |
| Stage 6 | Reflection Loop - Loop detection and error handling |
| Stage 7 | The Orchestrator - Complete agent integration |

---

## Quick Start

```bash
# 1. Run the setup script from the project root
bash scripts/setup.sh

# 2. Activate the virtual environment (optional but recommended)
source .venv/bin/activate

# 3. Run an example
python3 examples/stage0/exercise_1.py
```

## Running Individual Examples

All examples must be run from the **project root directory** (not from within `examples/`):

```bash
# Run a single example
python3 examples/stage0/exercise_1.py

# Run all examples for a specific stage
for i in {1..7}; do python3 examples/stage0/exercise_$i.py; done

# Run all examples across all stages
for stage in stage0 stage1 stage2 stage3 stage4 stage5 stage6 stage7; do
  for i in {1..7}; do
    python3 examples/$stage/exercise_$i.py
  done
done
```

## Stage 0: The API Foundation

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Make Your First API Call - Basic request/response cycle |
| `exercise_2.py` | 2 | Experiment with Temperature - How temperature affects creativity |
| `exercise_3.py` | 3 | System Prompt Power - How system prompts change response style |
| `exercise_4.py` | 4 | Multi-Turn Conversation - Maintaining conversation history |
| `exercise_5.py` | 5 | Max Tokens Limitation - What happens when you hit token limits |
| `exercise_6.py` | 6 | Error Handling - How the API responds to invalid requests |
| `exercise_7.py` | 7 | Token Cost Calculation - Understanding API usage costs |

## Stage 1: Raw Sensor

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Measure Token Latency - Tracking token count and timing |
| `exercise_2.py` | 2 | Inter-Token Latency - Measuring time between tokens |
| `exercise_3.py` | 3 | Time-To-First-Token - Measuring TTFT |
| `exercise_4.py` | 4 | Response Summary - Generating summary statistics |
| `exercise_5.py` | 5 | Streaming vs Non-Streaming - Comparing response modes |
| `exercise_6.py` | 6 | Multiple Prompts - Running several requests in sequence |
| `exercise_7.py` | 7 | Performance Profiling - Comprehensive performance analysis |

## Stage 2: Thinking Observer

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Simulated Thinking Block Parsing - Detecting thinking vs answer |
| `exercise_2.py` | 2 | Real Stream Thinking Detection - Live thinking observation |
| `exercise_3.py` | 3 | Thinking Content Extraction - Getting thinking content |
| `exercise_4.py` | 4 | Multiple Thinking Patterns - Different thinking block formats |
| `exercise_5.py` | 5 | Thinking Length Analysis - Measuring thinking content |
| `exercise_6.py` | 6 | Edge Cases - Handling missing or malformed thinking |
| `exercise_7.py` | 7 | Thinking vs Answer Comparison - Comparing both content types |

## Stage 3: State Engine

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Basic State Management - Understanding state growth |
| `exercise_2.py` | 2 | Context Window Limits - What happens at limits |
| `exercise_3.py` | 3 | System Instructions - Different system prompt effects |
| `exercise_4.py` | 4 | Message History - Full conversation history inspection |
| `exercise_5.py` | 5 | State Compilation - Understanding payload format |
| `exercise_6.py` | 6 | Error Handling in State - Managing state errors |
| `exercise_7.py` | 7 | State Summary - Comprehensive state analysis |

## Stage 4: Parsing Bridge

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Basic Stream Parsing - Detecting tool calls in streams |
| `exercise_2.py` | 2 | Multiple Tool Calls - Parsing multiple calls |
| `exercise_3.py` | 3 | Partial JSON Handling - Handling incomplete JSON |
| `exercise_4.py` | 4 | Tool Schema Integration - Using tool schemas |
| `exercise_5.py` | 5 | Buffer Management - Understanding pending text |
| `exercise_6.py` | 6 | Edge Cases - Handling malformed input |
| `exercise_7.py` | 7 | Performance Analysis - Parsing speed measurement |

## Stage 5: Sandboxed Hand

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Basic Tool Registration - How tools are registered |
| `exercise_2.py` | 2 | Tool Execution - Running registered tools |
| `exercise_3.py` | 3 | Error Handling in Tools - Tool error management |
| `exercise_4.py` | 4 | Type Safety - Type annotation handling |
| `exercise_5.py` | 5 | Custom Tool Development - Building new tools |
| `exercise_6.py` | 6 | Tool Schema Generation - Schema format understanding |
| `exercise_7.py` | 7 | Registry Analysis - Comprehensive registry inspection |

## Stage 6: Reflection Loop

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Basic Loop Detection - Identifying repeating patterns |
| `exercise_2.py` | 2 | Window Size Effects - How window size affects detection |
| `exercise_3.py` | 3 | Repetition Threshold - Threshold tuning |
| `exercise_4.py` | 4 | Backtracking - Restoring state after loops |
| `exercise_5.py` | 5 | Error Formatting - Error message formatting |
| `exercise_6.py` | 6 | Complex Loop Patterns - Detecting complex patterns |
| `exercise_7.py` | 7 | Loop Detection Analysis - Comprehensive analysis |

## Stage 7: The Orchestrator

| File | Exercise | Topic |
|------|----------|-------|
| `exercise_1.py` | 1 | Basic Orchestrator Run - How components work together |
| `exercise_2.py` | 2 | Interactive Session - Tool selection decision making |
| `exercise_3.py` | 3 | Multi-Turn Conversation - Context retention testing |
| `exercise_4.py` | 4 | Add Custom Tools - Extending with new functionality |
| `exercise_5.py` | 5 | Configure Agent Behavior - Configuration effects |
| `exercise_6.py` | 6 | Add Thinking Visualization - Reasoning insights |
| `exercise_7.py` | 7 | Build a ReAct Agent - Reason-Act-Observe pattern |
| `exercise_8.py` | 8 | Add Logging and Tracing - Debugging metrics |

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