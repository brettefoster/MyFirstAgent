# Stage 3: The Parsing Bridge

**Goal:** Build a robust, real-time parser that scans streaming chunks for specific markup patterns or JSON declarations.

## Conceptual Grounding

When an LLM wants to use a tool, it doesn't "call" a function. Instead, it outputs text that *describes* the function call. Your job is to detect this text in real-time and intercept it before it's displayed to the user.

## The Parsing Challenge

```
                      +-----------------------------+
                      |      Incoming Token Stream   |
                      +-----------------------------+
                                      │
                                      ▼
                      +-----------------------------+
                      |     Stream Parser Buffer    |
                      +-----------------------------+
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
          [No Matching Pattern]                [Matches Pattern]
                     │                                 │
                     ▼                                 ▼
            Print to Developer Console         Halt UI Output & 
                                               Extract Tool Parameters
```

## What You'll Learn

1. How to parse streaming text in real-time
2. Why you can't wait for the LLM to "finish"
3. How to use regex and JSON parsing on incomplete data
4. The concept of "action schemas" for tool calls

## Files

- `stream_parser.py` - Complete example implementation
- `exercises.md` - Interactive verification exercises

## Key Insight

> "We don't wait for the LLM to finish speaking to know it wants to act. We must parse the stream live."