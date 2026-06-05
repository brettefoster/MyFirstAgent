# Stage 5: The Reflection Loop

**Goal:** Build self-correction, loop detection, and backtracking mechanisms.

## Conceptual Grounding

Errors are not system crashes; they are context cues for the LLM to rewrite its own steps. The reflection loop is what makes an agent "intelligent" - it can learn from its mistakes and adjust its approach.

## The Reflection Loop

```
+----------------+      +------------------+      +------------------+
|  Execute Tool  |  --> |  Check Result    |  --> |  Success?        |
+----------------+      +------------------+      +------------------+
                                                    │
                        +-------------------+       │ No
                        │  Loop Detected?   │<──────┘
                        +-------------------+
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            [Yes: Backtrack]        [No: Retry with
             Feed Error to LLM        corrected context]
```

## What You'll Learn

1. How to detect infinite loops in agent execution
2. How to format errors as context for the LLM
3. How to implement backtracking and retry logic
4. How to add exponential backoff for rate limits

## Files

- `loop_detector.py` - Loop detection and backtracking
- `exercises.md` - Interactive verification exercises

## Key Insight

> "Errors are not system crashes; they are just context cues for the LLM to rewrite its own steps."