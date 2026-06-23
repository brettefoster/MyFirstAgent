# Stage 2: The Thinking Pattern Observer

**Goal:** Understand how models express reasoning before answering, and learn to detect thinking patterns in streaming output.

## Conceptual Grounding

Modern LLMs often exhibit "thinking" behavior - they reason through problems before providing answers. This can manifest as:

1. **Explicit thinking blocks** - Some models wrap reasoning in tags like `<thinking>...</thinking>`
2. **Chain-of-thought** - Natural language reasoning that precedes the answer
3. **Internal monologue** - Self-talk patterns like "Let me think about this..."

Understanding these patterns is crucial for:
- Building agents that can "show their work"
- Detecting when a model is reasoning vs. answering
- Parsing structured outputs from unstructured text

## Thinking Patterns in the Wild

### Pattern 1: XML-style Thinking Blocks

```
<thinking>
The user is asking about quantum computing. I need to explain it simply.
Quantum computing uses qubits instead of bits. Qubits can be in superposition.
I should mention key concepts: superposition, entanglement, quantum gates.
</thinking>

Quantum computing is a type of computation that uses quantum mechanical phenomena...
```

### Pattern 2: Chain-of-Thought Reasoning

```
To solve this problem, let me break it down step by step:

Step 1: First, I need to understand what the user is asking...
Step 2: Then I'll consider the relevant information...
Step 3: Finally, I can provide a complete answer...

Based on my analysis, the answer is...
```

### Pattern 3: Self-Correction

```
The capital of France is... wait, let me double-check. Yes, Paris is correct.
Actually, I should verify this. Paris has been the capital since...
```

## What You'll Learn

1. How to detect thinking patterns in streaming text
2. How to separate "reasoning" from "final answer"
3. How to visualize the model's thought process in real-time
4. Why thinking patterns improve complex reasoning tasks
5. How to prompt models for explicit thinking output

## Files

- `thinking_observer.py` - Thinking pattern detection and visualization
- `exercises.md` - Interactive verification exercises

## Configuration

Set your API endpoint in `.env`:

```bash
API_BASE=http://localhost:11434
MODEL=llama3
API_KEY=ollama
```

## Key Insight

> "Thinking patterns are the model's way of doing 'scratchpad' work. By observing them, you see how the model arrives at answers."

## Architecture

```
+------------------+      +-------------------+      +------------------+
|  Streaming Input | -->  |  Pattern Detector | -->  |  Thinking/Answer |
|  (token chunks)  |      |  (regex/buffer)   |      |  Separation      |
+------------------+      +-------------------+      +------------------+
                                        |
                                        v
                              +-------------------+
                              |  Visualization    |
                              |  (different colors)|
                              +-------------------+