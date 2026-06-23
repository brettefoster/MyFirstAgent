# Stage 8: The Final Agent

**Goal:** Assemble all stages into a complete, working agent.

## Conceptual Grounding

This is where all the pieces come together. You now have:
- **Stage 0:** Basic API request/response understanding
- **Stage 1:** Raw streaming from an OpenAI-compatible API
- **Stage 2:** Thinking pattern detection and visualization
- **Stage 3:** Conversation state management
- **Stage 4:** Real-time tool call parsing
- **Stage 5:** Sandboxed tool execution
- **Stage 6:** Reflection and loop detection
- **Stage 7:** The Orchestrator (integration layer)

Stage 8 is the culmination - a complete agent that demonstrates all the patterns learned.

## API Configuration

This agent uses a generic OpenAI-compatible API client. Configure your endpoint in `.env`:

```bash
# For local Ollama
API_BASE=http://localhost:11434
MODEL=llama3

# For Groq (cloud)
# API_BASE=https://api.groq.com/openai
# MODEL=llama3-70b-8192

# For vLLM
# API_BASE=http://localhost:8000
# MODEL=your-model-name
```

## The Complete Agent Architecture

```
+---------------------------------------------------------------+
|                        FINAL AGENT                            |
+---------------------------------------------------------------+
                              │
        +---------------------+---------------------+
        │                     │                     │
        ▼                     ▼                     ▼
+---------------+    +----------------+    +------------------+
|  Stage 0      |    |  Stage 1      |    |  Stage 2         |
|  API Basics   |    |  Raw Stream   |    |  Thinking        |
+---------------+    +----------------+    +------------------+
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
        +---------------------+---------------------+
        │                     │                     │
        ▼                     ▼                     ▼
+---------------+    +----------------+    +------------------+
|  Stage 3      |    |  Stage 4      |    |  Stage 5         |
|  State        |    |  Parser       |    |  Sandbox         |
+---------------+    +----------------+    +------------------+
                              │
                              ▼
        +---------------------+---------------------+
        │                     │                     │
        ▼                     ▼                     ▼
+---------------+    +----------------+    +------------------+
|  Stage 6      |    |  Stage 7      |    |  Stage 8         |
|  Reflection   |    |  Orchestrator |    |  Final Agent     |
+---------------+    +----------------+    +------------------+
```

## What You'll Build

A complete agent that:
1. Streams responses in real-time
2. Manages conversation history
3. Detects and executes tool calls
4. Runs tools in a sandbox
5. Handles errors and loops gracefully
6. Observes thinking patterns
7. Orchestrates all components

## Files

- `agent.py` - Complete agent implementation
- `exercises.md` - Final integration exercises

## Key Insight

> "The whole is greater than the sum of its parts. Each stage solves a specific problem; together they create a capable agent."