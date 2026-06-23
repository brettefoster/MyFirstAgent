# Stage 1: The Raw Sensor

**Goal:** Strip away SDK wrappers and read the raw Server-Sent Events (SSE) streaming directly from an OpenAI-compatible API.

## Conceptual Grounding

When you call an LLM SDK like `openai` or `google-genai`, it wraps standard network requests in high-level classes. This hides the reality that the LLM communication protocol is a simple HTTP POST request that streams back individual chunks of text formatted as Server-Sent Events (SSE).

In this stage, you'll write a raw HTTP client that witnesses the raw JSON packets containing the generated tokens as they land in the network buffer.

## The Streaming Endpoint

Works with any OpenAI-compatible endpoint:

- **Ollama**: `http://localhost:11434/v1/chat/completions`
- **vLLM**: `http://localhost:8000/v1/chat/completions`
- **Groq**: `https://api.groq.com/openai/v1/chat/completions`

## Request Payload Format (OpenAI-compatible)

```json
{
  "model": "llama3",
  "messages": [
    { "role": "user", "content": "Why is the sky blue?" }
  ],
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": true
}
```

## What You'll Learn

1. How HTTP streaming works at the protocol level
2. What Server-Sent Events (SSE) look like in raw form
3. How to parse OpenAI-style JSON responses from the API
4. The difference between the SDK abstraction and the actual wire format
5. How to work with any OpenAI-compatible model/provider
6. **NEW:** Timing metrics (TTFT, inter-token latency)
7. **NEW:** Chunk-by-chunk visualization

## Files

- `raw_stream.py` - Complete streaming implementation with timing metrics
- `exercises.md` - Interactive verification exercises

## Configuration

Set your API endpoint in `.env`:

```bash
API_BASE=http://localhost:11434
MODEL=llama3
API_KEY=ollama  # Often not required for local deployments
```

## Key Metrics Explained

| Metric | Description | Why It Matters |
|--------|-------------|----------------|
| **TTFT** (Time to First Token) | Time from request to first token received | Indicates model "thinking" time |
| **Inter-Token Latency** | Time between consecutive tokens | Shows generation speed |
| **Tokens/Second** | Generation throughput | Performance benchmarking |

## Key Insight

> "The LLM has no idea who I am; it's just predicting the next word character-by-character."