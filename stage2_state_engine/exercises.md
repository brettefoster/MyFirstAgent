# Stage 2 Exercises

## Exercise 1: Context Window Growth

**Task:** Modify `state_machine.py` to track and display the context size after each message. Create a conversation with 10+ exchanges and observe how the payload size grows.

**Question to answer:** At what point does the context size become a concern? What strategies could you use to manage this?

## Exercise 2: Implement Message Truncation

**Task:** Add a method to `AgentState` that truncates old messages when the context size exceeds a limit.

**Hint:** You might want to keep only the most recent N messages, or implement a "sliding window" approach.

**Expected behavior:**
```python
agent = AgentState()
agent.set_max_context_size(10000)  # 10KB limit
# After adding messages, old ones are automatically removed
```

## Exercise 3: Add System Messages

**Task:** Extend the `AgentState` class to support system-level messages that don't count toward conversation history but are prepended to every request.

**Use case:** You might want to inject "You are an expert in Python programming" as a system message for specific tasks.

## Exercise 4: Conversation Summarization

**Task:** Implement a method that summarizes old conversation history and replaces it with a condensed version.

**Example:**
```
Original: [user: "What is Python?", model: "Python is...", user: "How do I...", model: "You can..."]
Summarized: [system: "User is learning Python basics", user: "How do I write a function?"]
```

## Exercise 5: Build a Real Chat

**Task:** Combine Stage 1 and Stage 2 to create a working chat application:

1. Use `AgentState` to manage history
2. Use the raw streaming from Stage 1
3. Display responses in real-time
4. Allow the user to have a multi-turn conversation

**Hint:** You'll need to parse the stream and add each token to the model message as it arrives.