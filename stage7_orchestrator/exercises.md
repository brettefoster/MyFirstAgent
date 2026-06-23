# Stage 7: Exercises

## Exercise 1: Basic Orchestrator Run

Run the orchestrator demo:

```bash
python stage7_orchestrator/orchestrator.py
```

**Observe:** How do all the components work together? What is the flow of execution?

---

## Exercise 2: Interactive Session

Run the orchestrator in interactive mode:

```bash
python stage7_orchestrator/orchestrator.py --interactive
```

**Try these queries:**
1. "What's the weather in Paris?"
2. "Calculate 25 * 4"
3. "What time is it?"
4. "Search for Python tutorials"

**Question:** How does the agent decide which tool to use?

---

## Exercise 3: Multi-Turn Conversation

Modify the orchestrator to maintain conversation state across multiple user queries:

```python
def demo_multi_turn():
    config = AgentConfig()
    orchestrator = Orchestrator(config)
    
    # First turn
    response1 = orchestrator.run("My name is Alice.")
    print(f"Agent: {response1.content}")
    
    # Second turn (should remember name)
    response2 = orchestrator.run("What is my name?")
    print(f"Agent: {response2.content}")
```

**Question:** Does the agent remember context across turns?

---

## Exercise 4: Add Custom Tools

Extend the orchestrator with your own tools:

```python
def _register_custom_tools(self) -> None:
    @self.registry.register
    def get_quote() -> str:
        """Get a random inspirational quote."""
        quotes = [
            "The only way to do great work is to love what you do.",
            "Innovation distinguishes between a leader and a follower.",
            "Life is what happens when you're busy making other plans."
        ]
        import random
        return f"Quote: {random.choice(quotes)}"
```

**Test:** Ask the agent to "give me an inspirational quote"

---

## Exercise 5: Configure Agent Behavior

Experiment with different configurations:

```python
configs = [
    AgentConfig(temperature=0.1),  # Deterministic
    AgentConfig(temperature=0.7),  # Balanced
    AgentConfig(temperature=1.5),  # Creative
    AgentConfig(max_iterations=3),  # Limited tool calls
    AgentConfig(enable_loop_detection=False),  # No loop detection
]

for config in configs:
    orchestrator = Orchestrator(config)
    # Test with same query, observe differences
```

**Question:** How does temperature affect tool selection?

---

## Exercise 6: Add Thinking Visualization

Enhance the orchestrator to display thinking content separately:

```python
def run_with_thinking(self, user_message: str) -> AgentResponse:
    response = self.run(user_message)
    
    if response.thinking_content:
        print("\n" + "=" * 40)
        print("THINKING PROCESS:")
        print("=" * 40)
        print(response.thinking_content)
        print("=" * 40 + "\n")
    
    return response
```

**Question:** What insights does the thinking content provide?

---

## Exercise 7: Build a ReAct Agent

Implement the ReAct (Reason + Act) pattern:

```python
class ReActOrchestrator(Orchestrator):
    def run(self, user_message: str) -> AgentResponse:
        # ReAct loop: Reason -> Act -> Observe -> Repeat
        
        thought = self._generate_thought(user_message)
        print(f"Thought: {thought}")
        
        action = self._decide_action(thought)
        print(f"Action: {action}")
        
        observation = self._execute_action(action)
        print(f"Observation: {observation}")
        
        # Continue until final answer
        return self._synthesize_answer(thought, observation)
```

**Question:** How does ReAct differ from the standard agent loop?

---

## Exercise 8: Add Logging and Tracing

Build comprehensive logging for the agent:

```python
import logging

class LoggedOrchestrator(Orchestrator):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = logging.getLogger("agent")
        
    def run(self, user_message: str) -> AgentResponse:
        self.logger.info(f"User message: {user_message}")
        
        # Log each step
        self.logger.debug(f"State size: {len(self.state)}")
        self.logger.debug(f"Available tools: {[t.name for t in self.registry.tools]}")
        
        # ... rest of implementation
```

**Question:** What metrics are most useful for debugging?

---

## Verification Checklist

- [ ] Ran basic orchestrator demo
- [ ] Completed interactive session
- [ ] Built multi-turn conversation
- [ ] Added custom tools
- [ ] Experimented with configurations
- [ ] Visualized thinking process
- [ ] Implemented ReAct pattern
- [ ] Added logging and tracing

---

## Next Steps

Once you complete these exercises, you've mastered the core agent building patterns! Consider exploring **Stage 8: Advanced Patterns** for multi-agent systems, planning strategies, and human-in-the-loop workflows.