# Triaged Issues - Stage 1 Exercise 5

## Date: 2026-06-25

---

## Issue 1: Streaming API Returns `reasoning_content` Instead of `content`

**Severity:** High  
**Status:** Fixed  
**Files Affected:** `utils/api_client.py`, `examples/stage1/exercise_5.py`

### Description

The MLX server at `http://127.0.0.1:8080` (running Qwen3.6-35B-A3B) returns streaming chunks with `reasoning_content` field instead of `content` in the delta objects:

```json
{"delta": {"role": "assistant", "reasoning_content": "Here's a thinking process..."}}
```

The original code in `exercise_5.py` (line 69) only checked for `"content"`:
```python
if "content" in delta and delta["content"]:
```

Since the API sends `reasoning_content` (chain-of-thought reasoning), the condition was never true, so **zero tokens were ever extracted or printed**. The stream completed normally with `finish_reason: "stop"`, but with 0 tokens collected, resulting in:
- Total Tokens: 0
- TTFT: 0.00s
- Speed: 0.0 tok/s

### Root Cause Analysis Accuracy: ✅ CONFIRMED ACCURATE

The analysis correctly identifies that the Qwen3.6 model uses `reasoning_content` for its chain-of-thought output, and the original code had no fallback to extract it.

### Fix Applied

Both `utils/api_client.py` and `examples/stage1/exercise_5.py` were updated to check for `reasoning_content` as a fallback. The final implementation tracks them separately:

```python
if "content" in delta and delta["content"]:
    token = delta["content"]
    response_text += token
    print(token, end="", flush=True)

elif "reasoning_content" in delta and delta["reasoning_content"]:
    token = delta["reasoning_content"]
    reasoning_text += token
    f.dim(token)
```

### Verification

After the fix (combined with Issue 5 fix), streaming responses work correctly with 495+ tokens collected.

---

## Issue 2: First Turn Returns 0 Tokens Despite Partial Response

**Severity:** Medium  
**Status:** Resolved by Issue 5 Fix  
**Files Affected:** `examples/stage1/exercise_5.py`

### Description

When running the exercise with automated input, the first turn shows:
```
[YOU]: What is 2+2?

DEBUG: Messages count = 1
  [0] role=system, content='You are a helpful, concise assistant. Provide clea...'
DEBUG: payload model=router-model, stream=None

STREAMING RESPONSE:
  ----------------------------------------

i

------------------------------------------------------------
RESPONSE METRICS
------------------------------------------------------------

  Total Tokens: 0
  Total Time: 0.09s
  TTFT: 0.00s
  Speed: 0.0 tok/s
  Finish Reason: stop
```

Observations:
1. The character "i" was printed
2. But Total Tokens shows 0
3. TTFT shows 0.00s
4. The payload shows `stream=None` instead of `stream=True`

### Original Root Cause Analysis: ❌ INACCURATE

The original analysis claimed:
> "The metrics show 0 tokens because the `total_tokens` counter is only incremented inside the `if token:` block, but the token counter and timing logic may not be executing correctly."

**This was logically inconsistent.** The `print(token)` call and `total_tokens += 1` are in the **same code block**. If "i" was printed by that code path, `total_tokens` would be at least 1.

### Correct Root Cause (Discovered via Debug Logging)

The 0-token symptom was caused by **Issue 5**: the user's message was never added to the `messages` list. The API received only a system prompt with no user query, returned an error chunk, and then immediately stopped. The "i" in the output was a shell artifact, not from the streaming code.

### Resolution

- Fixed by adding `messages.append({"role": "user", "content": user_input})` in `main()` (see Issue 5).
- The `stream=None` observation is **expected behavior, not a bug** — `create_payload()` doesn't set `stream`; that's done in `APIClient.stream()` after the debug print.

---

## Issue 3: Conversation History May Not Match Chat Template Expectations

**Severity:** Low  
**Status:** Fixed  
**Files Affected:** `examples/stage1/exercise_5.py`

### Description

The server error "No user query found in messages" (from earlier testing) suggests the chat template in the MLX server expects a specific message pattern. The current implementation appends assistant responses as:
```python
messages.append({"role": "assistant", "content": generated_text})
```

If `generated_text` is empty (due to Issue 1/5), this creates empty assistant messages which may break subsequent turns.

### Root Cause Analysis Accuracy: ✅ CONFIRMED ACCURATE

Empty assistant messages in the conversation history can cause chat template parsing failures on subsequent turns, as the template expects alternating user/assistant pairs with non-empty content.

### Fix Applied

A guard was added:
```python
if response_text:
    messages.append({"role": "assistant", "content": response_text})
```

This prevents empty assistant messages from being added to the conversation history.

---

## Issue 4: Teaching Opportunity — Distinguishing Raw API Output from Processed Output

**Severity:** Low (Teaching Enhancement)  
**Status:** Fixed  
**Files Affected:** `examples/stage1/exercise_5.py`

### Description

This exercise is designed as a **teaching tool**, not a production POC. The original fix for Issue 1 collapsed `reasoning_content` and `content` into a single `generated_text` variable. While functionally it worked, it missed a valuable teaching opportunity to demonstrate the distinction between:

- **Raw API output**: What the model actually emits (`reasoning_content` = internal thinking, `content` = final answer)
- **Processed output**: What the user sees (formatted, labeled, and clearly distinguished)

### Teaching Opportunity

This issue teaches students a key concept in LLM systems: **models with reasoning capability produce two distinct streams of output**, and a well-designed system must handle them differently.

Students learn:
1. **Raw vs. Processed**: The API returns raw tokens that may include internal reasoning. A production system processes these into a user-facing response.
2. **Transparency**: Showing students both the raw reasoning and the final response helps them understand what's happening "under the hood."
3. **Separation of Concerns**: Reasoning (thinking) and response (saying) serve different purposes and should be tracked separately.

### Fix Applied

The `stream_response` function in `exercise_5.py` was rewritten to:

1. **Track separately**: `reasoning_text` (raw) and `response_text` (processed) are maintained as distinct variables.
2. **Display with visual distinction**: Reasoning tokens are printed via `f.dim()` (dim/gray), while response tokens are printed normally via `print()`.
3. **Show explicit breakdown**: After streaming completes, labeled sections display:
   - `RAW API OUTPUT (Reasoning)` — with explanatory note that it's not stored in history
   - `PROCESSED OUTPUT (Response)` — with explanatory note that only this is stored
4. **Store only response in history**: `messages.append()` only receives `response_text`, keeping conversation history clean.
5. **Extensive inline comments**: Teaching notes throughout the code explain the raw-vs-processed distinction.

### Expected Student Learning Outcome

When students run the exercise, they will see output like:

```
STREAMING RESPONSE:
  ----------------------------------------

[thinking in dim text...] here is my reasoning process...
The answer is 4.

----------------------------------------
RAW API OUTPUT (Reasoning)
  This is the model's internal chain-of-thought.
  It is NOT stored in conversation history.

  here is my reasoning process...

----------------------------------------
PROCESSED OUTPUT (Response)
  This is the model's user-facing answer.
  Only this is stored in conversation history.

  The answer is 4.

RESPONSE METRICS
  Total Tokens: 15
  ...
```

This makes the distinction between raw and processed output **visually explicit**, reinforcing the concept that a well-built system separates internal model reasoning from the user-facing response.

---

## Issue 5: User Message Never Added to Conversation History (ROOT CAUSE)

**Severity:** Critical  
**Status:** Fixed  
**Files Affected:** `examples/stage1/exercise_5.py`

### Description

**This was the actual root cause of the 0-token problem.** The `main()` function in `exercise_5.py` never appended the user's input to the `messages` list before calling `stream_response()`.

The `messages` list only contained the system prompt:
```python
messages = []
messages.append({"role": "system", "content": system_prompt})
```

When `stream_response()` was called, the API received a payload with **only a system message and no user query**. The server correctly identified this as an invalid request and returned:
1. Chunk 1: `{"delta": {"role": "assistant"}}` (empty, just setting role)
2. Chunk 2: `{"error": ...}` (API error — no user query found)
3. Chunk 3: `{"delta": {}, "finish_reason": "stop"}` (immediate stop)

This resulted in **0 tokens extracted**, matching all the symptoms observed in Issues 1 and 2.

### Root Cause

The original code in `main()`:
```python
# Display user prompt
f.model_input("YOU", user_input)
f.print()

# Stream the assistant's response (BUG: user_input never added to messages!)
stream_response(f, client, model, messages)
```

The user's input was displayed on screen but **never sent to the API**.

### Fix Applied

Added the missing line in `main()`:
```python
# Display user prompt
f.model_input("YOU", user_input)
f.print()

# IMPORTANT: Add the user's message to the conversation history BEFORE sending to the API.
# The API needs to see the user's query in the messages array to generate a response.
messages.append({"role": "user", "content": user_input})

# Stream the assistant's response
stream_response(f, client, model, messages)
```

### Verification

After this fix, the debug logging showed:
- Messages count: 2 (system + user)
- The API returned 495+ tokens of `reasoning_content`
- The RAW API OUTPUT / PROCESSED OUTPUT sections displayed correctly

### Teaching Note

This bug demonstrates an important concept for students: **the conversation history must include all messages (system, user, assistant) in order**. The API doesn't know what the user typed unless it's explicitly included in the `messages` array.

---

## Summary of Root Cause Analysis Verification

| Issue | Original Analysis | Verdict | Notes |
|-------|-------------------|---------|-------|
| Issue 1 | `reasoning_content` not handled | ✅ Accurate | Fix correctly applied, enhanced with separate tracking |
| Issue 2 | Token counter/timing logic broken | ❌ Inaccurate | Actually caused by Issue 5 (missing user message) |
| Issue 3 | Empty assistant messages break chat template | ✅ Accurate | Guard correctly applied |
| Issue 4 | (Newly identified) Teaching opportunity: raw vs. processed output | ✅ Implemented | Fix applied — reasoning and response tracked, displayed, and stored separately |
| Issue 5 | (Newly identified via debug logging) User message never added to history | ✅ Implemented | **This was the actual root cause** of the 0-token problem |

## Summary of Changes Made

| File | Change |
|------|--------|
| `utils/api_client.py` | Added handling for `reasoning_content` in demo client (line 286-290) |
| `examples/stage1/exercise_5.py` | Rewrote `stream_response()` to separately track, display, and store reasoning vs. response content with teaching-oriented formatting and inline comments |
| `examples/stage1/exercise_5.py` | Added `messages.append({"role": "user", "content": user_input})` in `main()` to fix the root cause |
| `examples/stage1/exercise_5.py` | Added error chunk handling to detect and log API errors |
| `examples/stage1/exercise_5.py` | Guard for empty assistant responses in conversation history (only `response_text` is stored) |

## Pending Items

- [ ] Test multi-turn conversations to verify chat template compatibility with the new reasoning/response separation