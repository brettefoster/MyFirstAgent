# Stage 8 Exercises

## Exercise 1: Complete Integration Test

**Task:** Run the complete agent with a multi-step query:

```
"What's the weather in London and what time is it there?"
```

**Expected behavior:**
1. Agent detects two tool calls (get_weather, get_time)
2. Executes both tools
3. Returns a combined response

**Question:** What challenges arise when handling multiple tool calls?

## Exercise 2: Add Real Tools

**Task:** Replace the simulated tools with real implementations:

1. `search` - Use a real search API (e.g., DuckDuckGo, Google Custom Search)
2. `get_weather` - Use a real weather API (e.g., OpenWeatherMap)
3. `get_time` - Use a timezone-aware time library

**Hint:** Use `requests` for API calls and handle rate limits.

## Exercise 3: Build a Web Interface

**Task:** Create a simple web UI for the agent:

1. Use Flask or FastAPI for the backend
2. Create a simple HTML/JS frontend
3. Display streaming responses in real-time
4. Show tool call status

**Expected interface:**
```
+------------------------------------------+
|  My First Agent                          |
+------------------------------------------+
|  [User input field]  [Send]              |
+------------------------------------------+
|  Agent: Hello! How can I help?           |
|  [Tool: search(query="...")]             |
|  [Tool result: ...]                      |
|  Agent: Here's what I found...           |
+------------------------------------------+
```

## Exercise 4: Add Persistence

**Task:** Implement conversation persistence:

1. Save conversations to a database (SQLite or file-based)
2. Load previous conversations on startup
3. Allow the user to view conversation history

**Expected interface:**
```python
agent = FinalAgent(config, storage=SQLiteStorage("conversations.db"))
conversations = agent.storage.list_conversations()
```

## Exercise 5: Build a Plugin System

**Task:** Create a plugin system for extensibility:

1. Define a plugin interface
2. Allow loading plugins from a directory
3. Implement hot-reloading for plugins

**Expected interface:**
```python
# plugins/search.py
class SearchPlugin:
    name = "search"
    description = "Search the web"
    
    def execute(self, query: str) -> str:
        return search_web(query)

# In agent
agent.load_plugins("plugins/")
```

## Exercise 6: Performance Optimization

**Task:** Optimize the agent for performance:

1. Add caching for tool results
2. Implement parallel tool execution
3. Add response compression

**Hint:** Use `functools.lru_cache` for caching and `asyncio.gather` for parallel execution.

## Exercise 7: Error Handling

**Task:** Implement comprehensive error handling:

1. Handle API rate limits with exponential backoff
2. Add timeout for tool execution
3. Implement graceful degradation when tools fail

**Expected behavior:**
```
[Error: API rate limit exceeded]
[Retrying in 2s...]
[Success: Got response]
```

## Exercise 8: Testing

**Task:** Write tests for the agent:

1. Unit tests for each component
2. Integration tests for the full agent
3. Mock the API for testing

**Hint:** Use `pytest` and `unittest.mock`.

## Final Challenge: Deploy Your Agent

**Task:** Deploy your agent to a cloud platform:

1. Containerize with Docker
2. Deploy to a cloud platform (e.g., Heroku, AWS, GCP)
3. Add monitoring and logging

**Expected outcome:** A working agent accessible via a public URL.

**Note:** Deployment artifacts are included in this directory:
- `Dockerfile` - Containerization configuration
- `Procfile` - Heroku deployment configuration  
- `runtime.txt` - Python version specification
- `deploy.md` - Deployment and monitoring guide
