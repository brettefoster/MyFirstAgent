# Stage 0: The API Foundation

**Goal:** Understand the basic HTTP request/response cycle before streaming.

## Conceptual Grounding

Before diving into streaming, you need to understand the fundamental contract between your application and an LLM API. A non-streaming call returns a complete JSON response all at once, which is easier to inspect and understand.

This stage teaches you:
1. How to make a basic POST request to an LLM API
2. What the response JSON structure looks like
3. Key parameters: `model`, `messages`, `temperature`, `max_tokens`
4. How authentication works

## The Basic Request

```json
POST /v1/chat/completions
{
  "model": "llama3",
  "messages": [
    { "role": "user", "content": "Hello, how are you?" }
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

## Response Format

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "llama3",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm doing well, thank you for asking..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 45,
    "total_tokens": 57
  }
}
```

## Key Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `model` | Which model to use | `llama3`, `mistral`, `gpt-4` |
| `messages` | Conversation history | Array of `{role, content}` objects |
| `temperature` | Randomness in responses | `0.0` (deterministic) to `2.0` (creative) |
| `max_tokens` | Maximum output length | `100` to `4096+` |
| `stream` | Enable streaming | `true` or `false` (Stage 1+) |

## Message Roles

| Role | Purpose |
|------|---------|
| `system` | Sets the assistant's behavior/persona |
| `user` | Human input/questions |
| `assistant` | Model responses |

## What You'll Learn

1. How to construct a valid API request
2. How to parse the JSON response
3. What `finish_reason` values mean (`stop`, `length`, `content_filter`)
4. How to read token usage for cost tracking

## Files

- `api_basics.py` - Complete non-streaming implementation
- `exercises.md` - Interactive verification exercises

## Configuration

Set your API endpoint in `.env`:

```bash
API_BASE=http://localhost:11434
MODEL=llama3
API_KEY=ollama  # Often not required for local deployments
```

## Key Insight

> "Every streaming response is just many small non-streaming responses stitched together. Master the basics first."