# Stage 0: Exercises

## Exercise 1: Make Your First API Call

Run the basic script and observe the output:

```bash
python stage0_api_foundation/api_basics.py
```

**Questions to answer:**
1. What is the `finish_reason` in the response?
2. How many total tokens were used?
3. What does the `usage` object tell you?

---

## Exercise 2: Experiment with Temperature

Modify the `demo_temperature()` function to test additional temperature values:
- Try `temperature=0.0` (completely deterministic)
- Try `temperature=2.0` (maximum creativity)

**Observe:** How does the output change at different temperatures?

---

## Exercise 3: System Prompt Power

Create a new function that demonstrates different system prompts:

```python
def demo_different_personalities():
    """Show how system prompts affect responses."""
    # Test at least 3 different system prompts:
    # 1. "You are a helpful assistant."
    # 2. "You are a pirate."
    # 3. "You are a formal lawyer."
    
    user_message = "What should I eat for dinner?"
    
    # Make requests with each system prompt and compare outputs
```

**Question:** How dramatically does the system prompt change the response style?

---

## Exercise 4: Multi-Turn Conversation

Modify the API call to include conversation history:

```python
messages = [
    {"role": "user", "content": "My name is Alex."},
    {"role": "assistant", "content": "Nice to meet you Alex!"},
    {"role": "user", "content": "What is my name?"}
]
```

**Question:** Does the model remember the name? Why or why not?

---

## Exercise 5: Max Tokens Limitation

Test what happens when you hit the token limit:

```python
payload = create_payload(
    messages=[{"role": "user", "content": "Write a long story about a dragon."}],
    max_tokens=50  # Very short limit
)
```

**Observe:** What is the `finish_reason` when you hit the limit? How does the response look?

---

## Exercise 6: Error Handling

Try making a request with invalid parameters:
- Use an invalid model name
- Send an empty messages array
- Use a negative temperature

**Question:** What kind of error responses do you get from the API?

---

## Exercise 7: Token Cost Calculation

If your API charges per token, calculate the cost of a conversation:

```python
# Example pricing (check your provider's actual rates)
PROMPT_COST_PER_MILLION = 0.50  # $ per million tokens
COMPLETION_COST_PER_MILLION = 1.50

def calculate_cost(prompt_tokens, completion_tokens):
    prompt_cost = (prompt_tokens / 1_000_000) * PROMPT_COST_PER_MILLION
    completion_cost = (completion_tokens / 1_000_000) * COMPLETION_COST_PER_MILLION
    return prompt_cost + completion_cost
```

**Question:** How much would a 100-turn conversation cost if each turn uses ~500 tokens?

---

## Verification Checklist

- [ ] Successfully made a non-streaming API call
- [ ] Understood the response JSON structure
- [ ] Experimented with temperature settings
- [ ] Observed system prompt effects
- [ ] Tested conversation history
- [ ] Understood finish reasons
- [ ] Calculated token costs

---

## Next Steps

Once you complete these exercises, move to **Stage 1: The Raw Sensor** to learn about streaming responses.