# Stage 1: The Raw Sensor

**Goal:** Strip away SDK wrappers and read the raw Server-Sent Events (SSE) streaming directly from the Gemini API.

## Conceptual Grounding

When you call an LLM SDK like `google-genai`, it wraps standard network requests in high-level classes. This hides the reality that the LLM communication protocol is a simple HTTP POST request that streams back individual chunks of text formatted as Server-Sent Events (SSE).

In this stage, you'll write a raw HTTP client that witnesses the raw JSON packets containing the generated tokens as they land in the network buffer.

## The Streaming Endpoint

```
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:streamGenerateContent?key=${API_KEY}
```

## Request Payload Format

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "Why is the sky blue?" }
      ]
    }
  ]
}
```

## What You'll Learn

1. How HTTP streaming works at the protocol level
2. What Server-Sent Events (SSE) look like in raw form
3. How to parse nested JSON responses from the API
4. The difference between the SDK abstraction and the actual wire format

## Files

- `raw_stream.py` - Complete example implementation
- `exercises.md` - Interactive verification exercises

## Key Insight

> "The LLM has no idea who I am; it's just predicting the next word character-by-character."