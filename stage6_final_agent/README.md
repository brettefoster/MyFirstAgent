# Stage 6: The Final Agent

**Goal:** Assemble all stages into a complete, working agent.

## Conceptual Grounding

This is where all the pieces come together. You now have:
- **Stage 1:** Raw streaming from an OpenAI-compatible API
- **Stage 2:** Conversation state management
- **Stage 3:** Real-time tool call parsing
- **Stage 4:** Sandboxed tool execution
- **Stage 5:** Reflection and loop detection

Stage 6 is the orchestration layer that ties it all together.

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
|  Stage 1      |    |  Stage 2      |    |  Stage 3         |
|  Raw Stream   |    |  State Engine |    |  Parser          |
+---------------+    +----------------+    +------------------+
        │                     │                     │
        +---------------------+---------------------+
                              │
                              ▼
        +---------------------+---------------------+
        │                     │                     │
        ▼                     ▼                     ▼
+---------------+    +----------------+    +------------------+
|  Stage 4      |    |  Stage 5      |    |  Stage 6         |
|  Sandbox      |    |  Reflection   |    |  Orchestration   |
+---------------+    +----------------+    +------------------+
```

## What You'll Build

A complete agent that:
1. Streams responses in real-time
2. Manages conversation history
3. Detects and executes tool calls
4. Runs tools in a sandbox
5. Handles errors and loops gracefully

## Files

- `agent.py` - Complete agent implementation
- `exercises.md` - Final integration exercises

## Key Insight

> "The whole is greater than the sum of its parts. Each stage solves a specific problem; together they create a capable agent."