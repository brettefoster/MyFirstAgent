# My First Agent

A lesson plan for building an AI agent from scratch, organized into progressive stages.

## Overview

This project teaches you how to build a complete AI agent by breaking down the problem into manageable stages. Each stage focuses on a specific aspect of agent development.

## API Configuration

This project uses a generic OpenAI-compatible API client. You can use:

- **Ollama** (local): `http://localhost:11434`
- **vLLM** (local): `http://localhost:8000`
- **Groq** (cloud): `https://api.groq.com/openai`
- **Any other OpenAI-compatible endpoint**

Set your configuration in `.env`:

```bash
API_BASE=http://localhost:11434
MODEL=llama3
API_KEY=ollama  # Often not needed for local deployments
```

## The Stages

### Stage 1: Raw Sensor
**Goal:** Learn to stream raw responses from an OpenAI-compatible API.

- Understand the API structure
- Handle streaming responses
- Parse Server-Sent Events (SSE)
- Work with any model/provider

**Files:**
- `stage1_raw_sensor/raw_stream.py` - Complete streaming implementation
- `stage1_raw_sensor/exercises.md` - Interactive exercises

### Stage 2: State Engine
**Goal:** Build a conversation state machine to manage context.

- Track conversation history
- Manage message payloads
- Handle context window limits

**Files:**
- `stage2_state_engine/state_machine.py` - State management
- `stage2_state_engine/exercises.md` - Interactive exercises

### Stage 3: Parsing Bridge
**Goal:** Build a real-time parser for detecting tool calls.

- Parse streaming text for patterns
- Extract tool call arguments
- Handle incomplete JSON

**Files:**
- `stage3_parsing_bridge/stream_parser.py` - Parser implementation
- `stage3_parsing_bridge/exercises.md` - Interactive exercises

### Stage 4: Sandboxed Hand
**Goal:** Build a tool registry and safe execution environment.

- Register and validate tools
- Execute tools in a sandbox
- Capture stdout/stderr

**Files:**
- `stage4_sandboxed_hand/tool_registry.py` - Tool management
- `stage4_sandboxed_hand/sandbox.py` - Safe execution
- `stage4_sandboxed_hand/exercises.md` - Interactive exercises

### Stage 5: Reflection Loop
**Goal:** Implement self-correction and loop detection.

- Detect infinite loops
- Format errors for the LLM
- Implement backtracking

**Files:**
- `stage5_reflection_loop/loop_detector.py` - Loop detection
- `stage5_reflection_loop/exercises.md` - Interactive exercises

### Stage 6: Final Agent
**Goal:** Assemble all stages into a complete working agent.

- Integrate all components
- Run multi-step conversations
- Handle errors gracefully

**Files:**
- `stage6_final_agent/agent.py` - Complete agent
- `stage6_final_agent/exercises.md` - Final exercises

## Quick Start

### Prerequisites

- Python 3.8+
- An OpenAI-compatible API endpoint (local or cloud)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/brettefoster/MyFirstAgent.git
   cd MyFirstAgent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API endpoint:
   ```bash
   # Copy the example config
   cp .env.example .env
   
   # Edit .env with your settings
   # For Ollama (local):
   #   API_BASE=http://localhost:11434
   #   MODEL=llama3
   
   # For Groq (cloud):
   #   API_BASE=https://api.groq.com/openai
   #   MODEL=llama3-70b-8192
   ```

4. Run a stage:
   ```bash
   # Run Stage 1
   python stage1_raw_sensor/raw_stream.py
   
   # Run Stage 6 (Final Agent)
   python stage6_final_agent/agent.py
   
   # Interactive mode
   python stage6_final_agent/agent.py --interactive
   ```

## Project Structure

```
MyFirstAgent/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example            # Environment variables template
├── utils/                  # Shared utilities
│   └── api_client.py       # Generic OpenAI-compatible API client
│
├── stage1_raw_sensor/      # Streaming from API
│   ├── README.md
│   ├── raw_stream.py
│   └── exercises.md
│
├── stage2_state_engine/    # Conversation state
│   ├── README.md
│   ├── state_machine.py
│   └── exercises.md
│
├── stage3_parsing_bridge/  # Tool call parsing
│   ├── README.md
│   ├── stream_parser.py
│   └── exercises.md
│
├── stage4_sandboxed_hand/  # Tool execution
│   ├── README.md
│   ├── tool_registry.py
│   ├── sandbox.py
│   └── exercises.md
│
├── stage5_reflection_loop/ # Error handling
│   ├── README.md
│   ├── loop_detector.py
│   └── exercises.md
│
└── stage6_final_agent/     # Complete agent
    ├── README.md
    ├── agent.py
    └── exercises.md
```

## Learning Path

1. **Start with Stage 1** - Understand how to stream from the API
2. **Move to Stage 2** - Learn to manage conversation state
3. **Continue through each stage** - Each builds on the previous
4. **Complete the exercises** - Verify your understanding
5. **Build Stage 6** - Assemble everything into a working agent

## Key Concepts

- **Streaming:** Real-time token delivery from the API
- **State Management:** Tracking conversation history
- **Tool Calls:** How LLMs "act" in the world
- **Sandboxing:** Safe code execution
- **Reflection:** Self-correction and loop detection
- **OpenAI-Compatible APIs:** Works with any standard API endpoint

## Supported Models & Providers

| Provider | Base URL | Example Models |
|----------|----------|----------------|
| Ollama | `http://localhost:11434` | llama3, mistral, codellama |
| vLLM | `http://localhost:8000` | Any deployed model |
| Groq | `https://api.groq.com/openai` | llama3-70b, mixtral-8x7b |
| LocalAI | `http://localhost:8080` | Any compatible model |

## Contributing

Contributions are welcome! Feel free to:
- Add new stages
- Improve existing implementations
- Add more exercises
- Fix bugs

## License

MIT License - See LICENSE file for details.