# Stage 3: Exercises

## Exercise 1: Basic State Management

Run the state machine demo:

```bash
python stage2_state_engine/state_machine.py
```

**Observe:** How does the state grow with each message? What does the payload look like?

---

## Exercise 2: Multi-Turn Conversation

Create a function that simulates a longer conversation:

```python
def demo_long_conversation():
    agent = AgentState()
    
    # Simulate 5+ turns of conversation
    conversation = [
        ("user", "Hi, my name is Bob."),
        ("assistant", "Hello Bob! Nice to meet you."),
        ("user", "What do I do for work?"),
        ("assistant", "You're a software engineer."),
        # ... more turns
    ]
    
    for role, text in conversation:
        if role == "user":
            agent.add_user_message(text)
        else:
            agent.add_model_message(text)
    
    # Check if the agent remembers Bob's name
    print(f"Context size: {agent.get_context_size()}")
```

**Question:** How does context size grow with each turn?

---

## Exercise 3: Token Counting

Add a token counter to the state machine:

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars ≈ 1 token)."""
    return len(text) // 4

class AgentState:
    def __init__(self):
        self.history = []
        self.total_tokens = 0
    
    def add_user_message(self, text: str):
        self.history.append({"role": "user", "content": text})
        self.total_tokens += estimate_tokens(text)
```

**Question:** How many tokens would a 10-turn conversation use?

---

## Exercise 4: Context Window Limits

Implement a sliding window strategy:

```python
class SlidingWindowState(AgentState):
    def __init__(self, max_messages: int = 10):
        super().__init__()
        self.max_messages = max_messages
    
    def get_messages(self) -> List[Dict]:
        messages = super().get_messages()
        if len(messages) > self.max_messages:
            # Keep system message and last N-1 messages
            return [messages[0]] + messages[-(self.max_messages-1):]
        return messages
```

**Test:** What happens to conversation continuity with a small window?

---

## Exercise 5: System Prompt Engineering

Experiment with different system prompts:

```python
prompts = [
    "You are a helpful assistant.",
    "You are a concise assistant. Answer in one sentence.",
    "You are an expert software engineer. Use technical terminology.",
    "You are a friendly tutor. Explain concepts simply.",
]

for prompt in prompts:
    agent = AgentState(system_instruction=prompt)
    # Test with same user question, observe different responses
```

**Question:** How dramatically does the system prompt affect output?

---

## Exercise 6: Tool Observation Format

Extend the state machine to properly handle tool observations:

```python
def demo_tool_conversation():
    agent = AgentState()
    
    # User asks about weather
    agent.add_user_message("What's the weather in London?")
    
    # Model decides to use a tool
    agent.add_model_message("Let me check the weather for you.")
    
    # Tool execution result
    agent.add_tool_observation(
        tool_name="get_weather",
        tool_call_id="call_123",
        observation="15°C, partly cloudy"
    )
    
    # Show the complete payload
    print(json.dumps(agent.compile_payload(), indent=2))
```

**Question:** How does the tool role differ from assistant role?

---

## Exercise 7: Context Summarization

Build a summarization strategy for old messages:

```python
class SummarizedState(AgentState):
    def __init__(self, summary_threshold: int = 20):
        super().__init__()
        self.summary_threshold = summary_threshold
        self.summary = ""
    
    def maybe_summarize(self):
        if len(self.history) > self.summary_threshold:
            # Summarize older messages
            old_messages = self.history[:self.summary_threshold]
            self.summary = self._summarize(old_messages)
            self.history = self.history[self.summary_threshold:]
```

**Question:** What information is lost when summarizing?

---

## Verification Checklist

- [ ] Understood stateless nature of LLM APIs
- [ ] Implemented multi-turn conversation
- [ ] Added token counting
- [ ] Built sliding window strategy
- [ ] Experimented with system prompts
- [ ] Handled tool observations
- [ ] Implemented summarization strategy

---

## Next Steps

Once you complete these exercises, move to **Stage 4: The Parsing Bridge** (renumbered from current Stage 3) to learn about parsing streaming text for tool calls.