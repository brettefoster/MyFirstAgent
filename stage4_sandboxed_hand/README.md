# Stage 4: The Sandboxed Hand

**Goal:** Build a tool registry, execution system, and stdout capture mechanism.

## Conceptual Grounding

The LLM can't run code. Your application runs the code and feeds the text back to the LLM. This stage is about building the "hands" of your agent - the tools it can use to interact with the world.

## The Tool Execution Flow

```
+----------------+      +------------------+      +------------------+
|  LLM Request   |  --> |  Tool Registry   |  --> |  Sandboxed Exec  |
|  call_search() |      |  Validate Args   |      |  Run & Capture   |
+----------------+      +------------------+      +------------------+
                                                        │
                                                        ▼
+----------------+      +------------------+      +------------------+
|  Feed Result   |  <-- |  Format Output   |  <-- |  stdout/stderr   |
|  to LLM        |      |  for Context     |      |  as Observation  |
+----------------+      +------------------+      +------------------+
```

## What You'll Learn

1. How to build a tool registry system
2. How to safely execute code in a sandbox
3. How to capture stdout and errors
4. How to format tool output for the LLM

## Files

- `tool_registry.py` - Tool registration and validation
- `sandbox.py` - Safe code execution environment
- `exercises.md` - Interactive verification exercises

## Key Insight

> "The LLM can't run code. My application runs the code and feeds the text back to the LLM."