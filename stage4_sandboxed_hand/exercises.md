# Stage 4 Exercises

## Exercise 1: Build a Tool Registry

**Task:** Extend `tool_registry.py` to:

1. Support async tool functions
2. Add tool descriptions that are sent to the LLM
3. Implement tool chaining (one tool's output feeds into another)

**Hint:** Use `asyncio` for async support and add a `chains` property to track tool dependencies.

## Exercise 2: Implement a Real Sandbox

**Task:** The `sandbox.py` uses subprocess for isolation. Enhance it to:

1. Limit memory usage (use `resource` module on Unix)
2. Block network access during execution
3. Create a read-only filesystem for tool code

**Hint:** Use `subprocess.Popen` with `ulimit` or `cgroups` for resource limits.

## Exercise 3: Add System Tools

**Task:** Create a set of system tools that the agent can use:

1. `read_file(path)` - Read a file's contents
2. `write_file(path, content)` - Write to a file
3. `run_command(command)` - Execute a shell command
4. `list_directory(path)` - List directory contents

**Hint:** Wrap these in the sandbox to prevent dangerous operations.

## Exercise 4: Tool Output Formatting

**Task:** Implement smart formatting for tool outputs:

1. Truncate large outputs (e.g., > 1000 chars)
2. Add "..." indicators for truncated content
3. Format JSON outputs with syntax highlighting
4. Summarize long text outputs

**Expected behavior:**
```
Tool 'search' returned:
  [Truncated: 5000 chars -> 500 chars]
  - Result 1: Python tutorials...
  - Result 2: Learn Python...
  ... (3 more results)
```

## Exercise 5: Build a Complete Agent Loop

**Task:** Combine Stages 1-4 to create a working agent:

1. Stream from the API (Stage 1)
2. Manage conversation state (Stage 2)
3. Parse tool calls in real-time (Stage 3)
4. Execute tools in sandbox (Stage 4)

**Expected output:**
```
USER: What's the weather in London and what time is it?

MODEL: Let me check the weather...
[TOOL: get_weather(location="London")]
>>> Weather: 15°C, partly cloudy

MODEL: And the time is...
[TOOL: get_time()]
>>> Time: 2024-01-15 14:30:00

MODEL: The weather in London is 15°C and the time is 14:30.