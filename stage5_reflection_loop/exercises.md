# Stage 5 Exercises

## Exercise 1: Implement Loop Detection

**Task:** The `loop_detector.py` has basic loop detection. Extend it to:

1. Add semantic similarity using embeddings or text comparison
2. Implement pattern detection for more complex loops
3. Add a "loop confidence" score that increases with each repetition

**Hint:** Use `difflib.SequenceMatcher` for text similarity.

## Exercise 2: Build a Backtracking System

**Task:** Implement a backtracking system that:

1. Saves checkpoints at each step
2. Can restore to a previous state when a loop is detected
3. Tracks which approaches have been tried

**Expected interface:**
```python
backtracker = Backtracker()
backtracker.save_checkpoint()

# If loop detected:
backtracker.restore_previous()
backtracker.try_alternative_approach()
```

## Exercise 3: Error Feedback to LLM

**Task:** Implement smart error formatting that:

1. Extracts the root cause of errors
2. Suggests specific fixes
3. Formats the error in a way the LLM can understand

**Example:**
```
Error: "Connection timeout"
Root cause: Network unreachable
Suggestion: Try a different data source or check connectivity
```

## Exercise 4: Implement Retry with Backoff

**Task:** Add retry logic with exponential backoff:

1. Track retry counts per action
2. Implement exponential backoff (1s, 2s, 4s, 8s...)
3. Add a maximum retry limit

**Hint:** Use `time.sleep()` with `2 ** retry_count`.

## Exercise 5: Build a Complete Reflection Loop

**Task:** Combine all Stage 5 components into a working reflection loop:

1. Execute a tool
2. Check for success
3. If failed, format error and feed to LLM
4. If loop detected, backtrack and try alternative
5. Continue until success or max iterations

**Expected output:**
```
Step 1: search(query="Python")
  -> Success: Found 10 results

Step 2: analyze(data="results")
  -> Error: Could not parse JSON

[REFLECTION: Error detected]
  Root cause: Invalid JSON format
  Suggestion: Try fetching raw text instead

Step 3: fetch_raw(url="...")
  -> Success: Got text content

Step 4: analyze(data="text")
  -> Success: Analysis complete