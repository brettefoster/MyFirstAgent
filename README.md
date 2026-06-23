# My First Agent

A lesson plan for building an AI agent from scratch, organized into progressive stages.

## Overview

This project teaches you how to build a complete AI agent by breaking down the problem into manageable stages. Each stage focuses on a specific aspect of agent development, progressing from simple API calls to sophisticated agentic workflows.

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

### Stage 0: The API Foundation (NEW)
**Goal:** Understand the basic HTTP request/response cycle before streaming.

- Make non-streaming API calls
- Examine the full JSON response structure
- Understand key parameters: `model`, `messages`, `temperature`, `max_tokens`
- Learn about finish reasons and token usage

**Files:**
- `stage0_api_foundation/api_basics.py` - Basic API implementation
- `stage0_api_foundation/exercises.md` - Interactive exercises

### Stage 1: The Raw Sensor
**Goal:** Learn to stream and observe individual tokens as they arrive.

- Understand HTTP streaming at the protocol level
- Parse Server-Sent Events (SSE) from the API
- Measure timing metrics (TTFT, inter-token latency)
- Visualize chunk-by-chunk text accumulation

**Files:**
- `stage1_raw_sensor/raw_stream.py` - Complete streaming implementation
- `stage1_raw_sensor/exercises.md` - Interactive exercises

### Stage 2: The Thinking Pattern Observer (NEW)
**Goal:** Understand how models express reasoning before answering.

- Detect thinking patterns in streaming text (`<thinking>` blocks, chain-of-thought)
- Separate "reasoning" from "final answer"
- Visualize the model's thought process in real-time
- Understand why thinking patterns improve complex reasoning

**Files:**
- `stage2_thinking_observer/thinking_observer.py` - Thinking pattern detection
- `stage2_thinking_observer/exercises.md` - Interactive exercises

### Stage 3: The State Engine
**Goal:** Build a conversation state machine to manage context and memory.

- Track conversation history with message roles
- Manage context window growth
- Implement context management strategies (sliding window, summarization)
- Engineer effective system prompts

**Files:**
- `stage3_state_engine/state_machine.py` - State management
- `stage3_state_engine/exercises.md` - Interactive exercises

### Stage 4: The Parsing Bridge
**Goal:** Build a real-time parser for detecting tool calls in streaming text.

- Parse streaming text for patterns in real-time
- Handle incomplete JSON during streaming
- Detect both text-based and structured tool calls
- Extract tool call arguments as they arrive

**Files:**
- `stage4_parsing_bridge/stream_parser.py` - Parser implementation
- `stage4_parsing_bridge/exercises.md` - Interactive exercises

### Stage 5: The Sandboxed Hand
**Goal:** Build a tool registry and safe execution environment.

- Register tools with JSON Schema definitions
- Execute tools in a sandboxed environment
- Capture stdout/stderr as observations
- Generate OpenAI-compatible tool definitions

**Files:**
- `stage5_sandboxed_hand/tool_registry.py` - Tool management
- `stage5_sandboxed_hand/sandbox.py` - Safe execution
- `stage5_sandboxed_hand/exercises.md` - Interactive exercises

### Stage 6: The Reflection Loop
**Goal:** Implement self-correction, loop detection, and error handling.

- Detect infinite loops in agent execution
- Format errors as context cues for the LLM
- Implement backtracking and retry logic
- Add exponential backoff for rate limits

**Files:**
- `stage6_reflection_loop/loop_detector.py` - Loop detection
- `stage6_reflection_loop/exercises.md` - Interactive exercises

### Stage 7: The Orchestrator (NEW)
**Goal:** Assemble all stages into a complete, working agent with proper orchestration.

- Integrate streaming, state, parsing, tools, and reflection
- Manage the main agent execution loop
- Handle multi-turn conversations
- Configure agent behavior and capabilities

**Files:**
- `stage7_orchestrator/orchestrator.py` - Complete agent implementation
- `stage7_orchestrator/exercises.md` - Integration exercises

### Stage 8: The Final Agent
**Goal:** The culmination - a complete agent demonstrating all patterns.

- Full integration of all components
- Multi-turn conversation handling
- Tool execution with reflection
- Thinking pattern observation

**Files:**
- `stage8_final_agent/agent.py` - Complete agent implementation
- `stage8_final_agent/exercises.md` - Final integration exercises

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
   # Run Stage 0 (API Foundation)
   python stage0_api_foundation/api_basics.py
   
   # Run Stage 1 (Raw Sensor)
   python stage1_raw_sensor/raw_stream.py
   
   # Run Stage 7 (Orchestrator)
   python stage7_orchestrator/orchestrator.py
   
   # Run Stage 8 (Final Agent)
   python stage8_final_agent/agent.py
   
   # Interactive mode
   python stage7_orchestrator/orchestrator.py --interactive
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
├── stage0_api_foundation/  # Basic API request/response (NEW)
│   ├── README.md
│   ├── api_basics.py
│   └── exercises.md
│
├── stage1_raw_sensor/      # Streaming from API
│   ├── README.md
│   ├── raw_stream.py
│   └── exercises.md
│
├── stage2_thinking_observer/  # Thinking pattern detection (NEW)
│   ├── README.md
│   ├── thinking_observer.py
│   └── exercises.md
│
├── stage3_state_engine/    # Conversation state (renumbered)
│   ├── README.md
│   ├── state_machine.py
│   └── exercises.md
│
├── stage4_parsing_bridge/  # Tool call parsing (renumbered)
│   ├── README.md
│   ├── stream_parser.py
│   └── exercises.md
│
├── stage5_sandboxed_hand/  # Tool execution (renumbered)
│   ├── README.md
│   ├── tool_registry.py
│   ├── sandbox.py
│   └── exercises.md
│
├── stage6_reflection_loop/ # Error handling (renumbered)
│   ├── README.md
│   ├── loop_detector.py
│   └── exercises.md
│
├── stage7_orchestrator/    # Complete agent integration (NEW)
│   ├── README.md
│   ├── orchestrator.py
│   └── exercises.md
│
└── stage8_final_agent/     # Final culmination agent (renumbered)
    ├── README.md
    ├── agent.py
    └── exercises.md
```

## Learning Path

1. **Start with Stage 0** - Understand basic API request/response
2. **Move to Stage 1** - Learn streaming and timing metrics
3. **Continue to Stage 2** - Observe thinking patterns
4. **Build Stage 3** - Manage conversation state
5. **Continue through each stage** - Each builds on the previous
6. **Complete Stage 7/8** - Assemble everything into a working agent

## Key Concepts

| Concept | Description | Stage |
|---------|-------------|-------|
| **API Basics** | Request/response cycle, parameters | Stage 0 |
| **Streaming** | Real-time token delivery from the API | Stage 1 |
| **Thinking Patterns** | How models reason before answering | Stage 2 |
| **State Management** | Tracking conversation history | Stage 3 |
| **Tool Parsing** | Detecting tool calls in streaming text | Stage 4 |
| **Tool Execution** | Safe code execution and output capture | Stage 5 |
| **Reflection** | Self-correction and loop detection | Stage 6 |
| **Orchestration** | Integrating all components | Stage 7 |
| **Final Agent** | Complete working agent | Stage 8 |

## Supported Models & Providers

| Provider | Base URL | Example Models |
|----------|----------|----------------|
| Ollama | `http://localhost:11434` | llama3, mistral, codellama |
| vLLM | `http://localhost:8000` | Any deployed model |
| Groq | `https://api.groq.com/openai` | llama3-70b, mixtral-8x7b |
| LocalAI | `http://localhost:8080` | Any compatible model |

## What You'll Learn

By completing this lesson plan, you will understand:

1. **How LLM APIs work** - From basic requests to streaming responses
2. **How models "think"** - Observing reasoning patterns and chain-of-thought
3. **How agents use tools** - Parsing, executing, and observing tool calls
4. **How to handle errors** - Loop detection, backtracking, and self-correction
5. **How to build complete agents** - Orchestrating all components together

## Contributing

Contributions are welcome! Feel free to:
- Add new stages (especially Stage 9+: Advanced Patterns)
- Improve existing implementations
- Add more exercises
- Fix bugs

## License

MIT License - See LICENSE file for details.