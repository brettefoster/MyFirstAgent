# Stage 1 Exercises

## Exercise 1: Measure Token Latency

**Task:** The `raw_stream.py` script already calculates Time-To-First-Token (TTFT) and Inter-Token Latency. Modify the script to:

1. Track the total number of tokens received
2. Calculate the average tokens per second
3. Output a summary at the end of each response

**Expected Output:**
```
=== RESPONSE SUMMARY ===
Total Tokens: 25
Total Time: 3.2s
Tokens/Second: 7.8
TTFT: 0.8s
========================
```

## Exercise 2: Handle Streaming Errors

**Task:** Add error handling for:
1. Invalid API key (403 error)
2. Rate limiting (429 error)
3. Network timeouts

**Hint:** Check the HTTP status codes in the `HTTPError` handler and provide meaningful error messages.

## Exercise 3: Compare SDK vs Raw

**Task:** 
1. Install the OpenAI Python SDK: `pip install openai`
2. Write a script using the SDK to make the same request to your OpenAI-compatible endpoint
3. Compare the code complexity and output between the SDK version and raw version

**Question to answer:** What abstractions does the SDK provide, and what do you lose by using it?

## Exercise 4: Explore Different Models

**Task:** Modify the `MODEL` variable in your `.env` file to try different models available on your API endpoint:
- For Ollama: `llama3`, `mistral`, `codellama`
- For Groq: `llama3-70b-8192`, `mixtral-8x7b-32768`
- For vLLM: depends on your deployed model

**Observation:** Compare the token speeds and response quality between models.

## Exercise 5: Build a Chat Interface

**Task:** Extend the script to:
1. Accept user input from the command line (use `input()`)
2. Loop continuously, allowing multiple questions
3. Display only the parsed tokens (not the raw JSON)

**Hint:** Use a `while True` loop and break when the user types "quit".