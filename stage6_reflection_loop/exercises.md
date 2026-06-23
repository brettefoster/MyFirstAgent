# Stage 6: Exercises

## Exercise 1: Basic Loop Detection

Run the loop detector demo:

```bash
python stage5_reflection_loop/loop_detector.py
```

**Observe:** How does the detector identify repeating patterns?

---

## Exercise 2: Simulate an Infinite Loop

Create a simulation that triggers loop detection:

```python
def demo_infinite_loop():
    detector = LoopDetector(window_size=5)
    
    # Simulate repeated failed actions
    steps = [
        ExecutionStep(1, "search", {"query": "weather"}, {}, False, "Tool not found"),
        ExecutionStep(2, "search", {"query": "weather"}, {}, False, "Tool not found"),
        ExecutionStep(3, "search", {"query": "weather"}, {}, False, "Tool not found"),
    ]
    
    for step in steps:
        detector.add_step(step)
        result = detector.detect_loop()
        if result.is_loop:
            print(f"Loop detected! {result.pattern}")
            break
```

**Question:** How many repetitions are needed before a loop is detected?

---

## Exercise 3: Error Formatting

Build better error messages for the LLM:

```python
def format_error_for_llm(step: ExecutionStep, suggestion: str = None) -> str:
    """Format an error as actionable context for the LLM."""
    lines = [
        f"⚠️  Error in step {step.step_number}: {step.action}",
        f"   Input: {step.input_data}",
        f"   Error: {step.error}",
    ]
    
    if suggestion:
        lines.append(f"   💡 Suggestion: {suggestion}")
    
    return "\n".join(lines)
```

**Test:** How does the LLM respond to different error formats?

---

## Exercise 4: Exponential Backoff

Implement backoff for rate limits:

```python
import time

class RateLimitHandler:
    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_count = 0
    
    def get_delay(self) -> float:
        """Calculate delay with exponential backoff."""
        delay = min(self.base_delay * (2 ** self.retry_count), self.max_delay)
        return delay
    
    def wait_and_retry(self):
        """Wait and prepare for retry."""
        delay = self.get_delay()
        print(f"Rate limited. Waiting {delay}s...")
        time.sleep(delay)
        self.retry_count += 1
    
    def reset(self):
        """Reset retry count after success."""
        self.retry_count = 0
```

**Question:** What are good values for base_delay and max_delay?

---

## Exercise 5: Self-Evaluation

Add a self-evaluation step where the LLM critiques its own output:

```python
def evaluate_response(llm_response: str, user_request: str) -> str:
    """Ask the LLM to evaluate its own response."""
    evaluation_prompt = f"""
    Evaluate if your previous response adequately addressed this request:

    Request: {user_request}
    Response: {llm_response}

    Consider:
    1. Did you answer the question directly?
    2. Is the information accurate?
    3. Did you use appropriate tools?

    If the response is inadequate, explain what's missing and how to improve.
    """
    
    # Make API call to evaluate
    return call_llm(evaluation_prompt)
```

**Question:** Does self-evaluation improve response quality?

---

## Exercise 6: Recovery Strategies

Build different recovery strategies for different error types:

```python
class RecoveryStrategy:
    @staticmethod
    def handle_validation_error(error: str, original_args: dict) -> dict:
        """Fix validation errors by correcting arguments."""
        # Parse error and suggest fixes
        return original_args  # Modified
    
    @staticmethod
    def handle_tool_not_found(error: str, available_tools: list) -> str:
        """Suggest alternative tools."""
        return f"Tool not found. Available tools: {', '.join(available_tools)}"
    
    @staticmethod
    def handle_timeout(error: str) -> dict:
        """Simplify the request."""
        return {"simplify": True, "break_into_steps": True}
```

**Test:** Which strategies work best for different error types?

---

## Exercise 7: Execution History Tracking

Build a comprehensive execution tracker:

```python
@dataclass
class ExecutionTrace:
    steps: List[ExecutionStep]
    total_time: float
    tool_calls: int
    errors: int
    loops_detected: int
    
    def to_summary(self) -> str:
        return f"""
Execution Summary:
  Total Steps: {len(self.steps)}
  Duration: {self.total_time:.2f}s
  Tool Calls: {self.tool_calls}
  Errors: {self.errors}
  Loops: {self.loops_detected}
        """
```

**Question:** What metrics are most useful for debugging agents?

---

## Verification Checklist

- [ ] Understood loop detection mechanisms
- [ ] Simulated infinite loops
- [ ] Built error formatting for LLMs
- [ ] Implemented exponential backoff
- [ ] Added self-evaluation patterns
- [ ] Created recovery strategies
- [ ] Tracked execution history

---

## Next Steps

Once you complete these exercises, move to **Stage 7: The Orchestrator** (renumbered from current Stage 6) to learn about assembling all components into a complete agent.