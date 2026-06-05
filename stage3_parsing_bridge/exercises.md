# Stage 3 Exercises

## Exercise 1: Build a Real-Time Parser

**Task:** The `stream_parser.py` demonstrates parsing. Extend it to:

1. Support more complex tool schemas with nested objects
2. Add validation that parsed arguments match the schema
3. Handle cases where the LLM outputs malformed JSON

**Hint:** Use the `jsonschema` library for validation.

## Exercise 2: Integrate with Stage 1

**Task:** Combine the raw stream from Stage 1 with the parser from Stage 3:

1. Feed each token from the stream into the parser
2. When a tool call is detected, halt the display
3. Execute the tool and show the result

**Expected behavior:**
```
I'll help you with that. Let me search for...
[TOOL CALL DETECTED: search(query="best restaurants in Paris")]
>>> Executing search...
>>> Result: [search results]
Now I can tell you about the best restaurants...
```

## Exercise 3: Multiple Tool Call Formats

**Task:** The current parser uses `call_toolname({...})` format. Implement support for:

1. JSON-based tool calls: `{"tool": "search", "args": {"query": "..."}}`
2. XML-based tool calls: `<tool name="search"><query>...</query></tool>`
3. Markdown code blocks:
   ```
   ```json
   {"tool": "search", "args": {"query": "..."}}
   ```
   ```

**Question:** Which format is most robust for streaming? Why?

## Exercise 4: Handle Partial Matches

**Task:** The parser currently waits for complete JSON. Implement a "lookahead" mechanism:

1. When a tool call pattern is detected, buffer subsequent tokens
2. Only trigger the tool call when complete JSON is found
3. If the LLM changes its mind mid-stream, handle gracefully

**Hint:** Use a state machine to track parsing state (e.g., `WAITING_FOR_TOOL`, `BUFFERING_JSON`, `COMPLETE`).

## Exercise 5: Build a Tool Registry

**Task:** Create a `ToolRegistry` class that:

1. Stores available tools and their schemas
2. Validates parsed tool calls against schemas
3. Returns structured tool call objects

**Expected interface:**
```python
registry = ToolRegistry()
registry.register_tool(search_tool)

# In the parser:
tool_call = registry.parse_tool_call(detected_text)
if tool_call:
    registry.execute(tool_call)