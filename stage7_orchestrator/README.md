# Stage 7: The Orchestrator

**Goal:** Assemble all stages into a complete, working agent with proper orchestration.

## Conceptual Grounding

This is where all the pieces come together. You now have:
- **Stage 0:** Basic API request/response understanding
- **Stage 1:** Raw streaming from an OpenAI-compatible API
- **Stage 2:** Thinking pattern detection and visualization
- **Stage 3:** Conversation state management
- **Stage 4:** Real-time tool call parsing
- **Stage 5:** Sandboxed tool execution
- **Stage 6:** Reflection and loop detection

Stage 7 is the orchestration layer that ties it all together into a cohesive agent.

## The Complete Agent Architecture

```
+-----------------------------------------------------------------------+
|                           THE ORCHESTRATOR                            |
+-----------------------------------------------------------------------+
                                  │
        +-------------------------+-------------------------+
        │                         │                         │
        ▼                         ▼                         ▼
+---------------+         +----------------+         +------------------+
|  Streaming    |         |  State         |         |  Thinking        |
|  Layer        |         |  Engine        |         |  Observer        |
+---------------+         +----------------+         +------------------+
        │                         │                         │
        └─────────────────────┬───┴─────────────────────────┘
                              │
                              ▼
        +---------------------+---------------------+
        │                                         │
        ▼                                         ▼
+---------------+                         +------------------+
|  Parser       |                         |  Reflection      |
|  Bridge       |                         |  Loop            |
+---------------+                         +------------------+
        │                                         │
        ▼                                         │
+---------------+                                 │
|  Tool         |─────────────────────────────────┘
|  Execution    |
+---------------+
```

## The Agent Loop

```
1. RECEIVE: User message arrives
   │
   ▼
2. UPDATE STATE: Add user message to history
   │
   ▼
3. GENERATE: Stream response from LLM
   │
   ├─► OBSERVE THINKING: Detect and categorize reasoning
   │
   ▼
4. PARSE: Check for tool calls in stream
   │
   ├─► TOOL CALL DETECTED? ──YES──► EXECUTE TOOL
   │                                    │
   │                                    ▼
   │                              ADD OBSERVATION TO STATE
   │                                    │
   │                                    └──────┐
   │                                           │
   ▼                                          │
5. CHECK REFLECTION: Loop detection, errors │
   │                                         │
   ├─► LOOP/ERROR? ──YES──► FEED ERROR TO STATE ──┘
   │
   ▼ NO
6. COMPLETE: Return final response to user
```

## What You'll Learn

1. How to integrate all components into a working agent
2. How to manage state transitions in the agent loop
3. How to handle concurrent concerns (streaming + parsing + execution)
4. How to build an interactive agent session
5. **NEW:** Agent configuration and customization
6. **NEW:** Multi-turn conversation handling

## Files

- `orchestrator.py` - Complete agent implementation
- `exercises.md` - Integration exercises

## Configuration

```python
@dataclass
class AgentConfig:
    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    max_iterations: int = 10      # Max tool calls per turn
    max_tokens: int = 4096        # Max output tokens
    temperature: float = 0.7      # Creativity level
    enable_thinking_observation: bool = True
    enable_loop_detection: bool = True
```

## Key Insight

> "The whole is greater than the sum of its parts. Each stage solves a specific problem; together they create a capable agent."