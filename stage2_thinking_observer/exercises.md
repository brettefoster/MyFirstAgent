# Stage 2: Exercises

## Exercise 1: Simulated Thinking Block Parsing

Run the thinking observer script:

```bash
python stage2_thinking_observer/thinking_observer.py
```

**Observe:** How does the `ThinkingObserver` categorize different parts of the simulated stream?

---

## Exercise 2: Add Custom Thinking Patterns

Extend the `THINKING_START_PATTERNS` list in `ThinkingObserver`:

```python
THINKING_START_PATTERNS = [
    r"<thinking>",
    r"thought:",
    # Add your own patterns:
    r"#思考",  # Chinese "think"
    r"Let me analyze",
    r"My reasoning is",
]
```

**Test:** Create simulated chunks that use your new patterns and verify they're detected.

---

## Exercise 3: Real API Testing

Uncomment the `demo_streaming_with_thinking()` call in `main()`:

```python
def main():
    demo_simulated_thinking()
    demo_chain_of_thought()
    demo_streaming_with_thinking()  # Enable this
```

Run with a model that supports thinking (if available):

```bash
python stage2_thinking_observer/thinking_observer.py
```

**Question:** Does your model produce explicit thinking blocks? What patterns do you observe?

---

## Exercise 4: Build a Thinking Visualizer

Create a new function that visualizes thinking vs answer with different output:

```python
def demo_visualization():
    """Show thinking in a box, answer normally."""
    observer = ThinkingObserver()
    
    # Simulated stream
    chunks = [
        "<thinking>\nAnalyzing the problem...\n</thinking>\n\n",
        "The answer is 42."
    ]
    
    for chunk in chunks:
        segments = observer.feed_chunk(chunk)
        for seg in segments:
            if seg.mode == OutputMode.THINKING:
                print(f"[THINKING]: {seg.text}")
            else:
                print(f"[ANSWER]: {seg.text}")
```

**Goal:** Make the output visually distinct for each mode.

---

## Exercise 5: Thinking Metrics

Add metrics tracking to `ThinkingObserver`:

```python
@dataclass
class ThinkingMetrics:
    thinking_duration: float  # Time spent in thinking mode
    answer_duration: float    # Time spent in answer mode
    thinking_token_count: int
    answer_token_count: int
```

**Question:** What insights can you gain from measuring thinking vs answer time?

---

## Exercise 6: Prompt Engineering for Thinking

Experiment with prompts that encourage thinking behavior:

```python
prompts = [
    "What is 2+2?",  # Simple, no thinking
    "Think step by step: What is 2+2?",  # Encourages thinking
    "Show your work: Calculate 15 * 24",  # Explicit reasoning request
]

for prompt in prompts:
    # Make API call and observe output patterns
```

**Question:** Which prompts produce more explicit thinking patterns?

---

## Exercise 7: Hide Thinking from User

Build a wrapper that shows only the answer to users but logs thinking for debugging:

```python
class UserFacingAgent:
    def __init__(self):
        self.observer = ThinkingObserver()
    
    def stream_to_user(self, chunk):
        """Only show answer to user."""
        segments = self.observer.feed_chunk(chunk)
        for seg in segments:
            if seg.mode == OutputMode.ANSWER:
                print(seg.text, end="", flush=True)
            # Thinking is silently logged
    
    def get_debug_log(self):
        """Return full thinking process for debugging."""
        return self.observer.get_thinking_content()
```

**Use case:** Show clean output to users while preserving reasoning for analysis.

---

## Verification Checklist

- [ ] Understood thinking pattern detection
- [ ] Added custom patterns to the observer
- [ ] Tested with real API (if possible)
- [ ] Built a visualizer for thinking vs answer
- [ ] Added metrics tracking
- [ ] Experimented with prompt engineering
- [ ] Created user-facing wrapper

---

## Next Steps

Once you complete these exercises, move to **Stage 3: The State Engine** (renumbered from current Stage 2) to learn about conversation state management.