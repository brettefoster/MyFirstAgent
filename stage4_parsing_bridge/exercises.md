# Stage 4: Exercises

## Exercise 1: Basic Stream Parsing

Run the stream parser demo:

```bash
python stage3_parsing_bridge/stream_parser.py
```

**Observe:** How does the parser detect tool calls in the simulated stream?

---

## Exercise 2: Add New Tool Patterns

Extend the parser to detect a new tool:

```python
TOOL_SCHEMAS = [
    # ... existing tools ...
    {
        "name": "send_email",
        "description": "Send an email to a recipient",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email content"}
            },
            "required": ["to", "subject", "body"]
        }
    }
]
```

**Test:** Create simulated stream chunks that include `call_send_email({...})` and verify detection.

---

## Exercise 3: Incremental JSON Parsing

Build a parser that handles character-by-character streaming:

```python
def demo_character_stream():
    parser = StreamParser(TOOL_SCHEMAS)
    
    # Simulate character-by-character input
    text = 'call_search({"query": "Python tutorials"})'
    
    for char in text:
        detected = parser.feed_chunk(char)
        if detected:
            print(f"Detected after {len(text)} chars!")
            break
```

**Question:** How many characters are needed before the parser can confidently detect a tool call?

---

## Exercise 4: Handle Nested JSON

Test the parser with complex nested arguments:

```python
complex_call = '''call_search({
    "query": "Python tutorials",
    "filters": {
        "language": "en",
        "min_rating": 4.5
    },
    "tags": ["beginner", "interactive"]
})'''
```

**Question:** Does your parser handle nested JSON correctly?

---

## Exercise 5: Partial/Incomplete JSON

Test how the parser handles incomplete tool calls:

```python
incomplete_chunks = [
    "call_search({",
    '"query": "',
    "test",
]  # Missing closing brace and parenthesis
```

**Question:** What happens when the JSON is incomplete? How can you improve handling?

---

## Exercise 6: Multiple Tool Calls

Test parsing multiple tool calls in one stream:

```python
multi_call_stream = [
    "I'll help with that. ",
    "call_search({\"query\": \"restaurants\"})",
    " Now let me check the weather. ",
    "call_get_weather({\"location\": \"Paris\"})",
]
```

**Question:** Does your parser correctly detect both tool calls?

---

## Exercise 7: Structured Tool Call Format

Many APIs return structured tool calls in the delta:

```python
# OpenAI-style structured tool call
delta = {
    "tool_calls": [
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "search",
                "arguments": '{"query": "Python tutorials"}'
            }
        }
    ]
}
```

Build a parser that handles both text-based AND structured tool calls:

```python
class HybridParser(StreamParser):
    def feed_chunk(self, chunk):
        # First check for structured tool calls
        if "tool_calls" in chunk:
            return self._parse_structured(chunk)
        # Fall back to text-based parsing
        return super().feed_chunk(chunk.get("content", ""))
```

---

## Verification Checklist

- [ ] Understood streaming parsing challenges
- [ ] Added new tool patterns
- [ ] Tested character-by-character streaming
- [ ] Handled nested JSON correctly
- [ ] Managed incomplete JSON gracefully
- [ ] Parsed multiple tool calls
- [ ] Built hybrid parser for structured + text formats

---

## Next Steps

Once you complete these exercises, move to **Stage 5: The Sandboxed Hand** (renumbered from current Stage 4) to learn about tool execution and sandboxing.