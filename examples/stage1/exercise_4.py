#!/usr/bin/env python3
"""
Example solution for Stage 1 Exercise 4: Explore Different Models

This script demonstrates how different models perform by:
1. Testing multiple models from your API endpoint
2. Comparing token speeds
3. Observing response quality differences

Usage:
  - Modify the MODEL variable in your .env file, or
  - Run with different model names as command-line arguments

For Ollama: llama3, mistral, codellama, etc.
For Groq: llama3-70b-8192, mixtral-8x7b-32768, etc.
For vLLM: depends on your deployed models
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration, API client, and formatter
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


# Default models to test - customize based on your endpoint
DEFAULT_MODELS = {
    # Ollama common models
    "llama3": "Llama 3 (default Ollama)",
    "mistral": "Mistral (default Ollama)",
    "codellama": "Code Llama (Ollama)",
    # Fallback generic names
    "default": "Default configured model",
}


def test_model(f, model_name, description, client, prompt, max_tokens=200):
    """
    Test a single model and collect performance metrics.

    Args:
        f: The Formatter instance.
        model_name: The model identifier.
        description: Human-readable description.
        client: The APIClient instance.
        prompt: The prompt to test with.
        max_tokens: Maximum tokens to generate.

    Returns:
        Dictionary with metrics, or None if the request failed.
    """
    f.subheader(f"MODEL: {model_name}")
    f.config(f"  Description: {description}")
    f.print()

    f.model_input("PROMPT", prompt)
    f.print()

    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=max_tokens,
        model=model_name,
    )

    f.raw_request(payload)

    start_time = time.time()
    last_token_time = start_time
    ttft = 0.0
    total_tokens = 0
    generated_text = ""

    f.script("STREAMING RESPONSE:")
    f.dim("  " + "-" * 40)
    f.print()

    try:
        for chunk in client.stream(payload):
            if "_raw" in chunk:
                continue

            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            if "content" in delta and delta["content"]:
                token = delta["content"]
                current_time = time.time()

                if total_tokens == 0:
                    ttft = current_time - start_time

                inter_token = current_time - last_token_time
                last_token_time = current_time
                total_tokens += 1

                generated_text += token
                print(token, end="", flush=True)

            if "finish_reason" in choice and choice["finish_reason"]:
                print(f"\n[Finish reason: {choice['finish_reason']}]")

        total_time = time.time() - start_time
        tps = total_tokens / total_time if total_time > 0 else 0

        f.print()
        f.subheader("MODEL PERFORMANCE METRICS")
        f.metadata("Total Tokens", str(total_tokens))
        f.metadata("Total Time", f"{total_time:.2f}s")
        f.metadata("Tokens/Sec", f"{tps:.2f}")
        f.metadata("TTFT", f"{ttft:.2f}s")
        f.metadata("Avg ITL", f"{(total_time / total_tokens if total_tokens > 0 else 0):.4f}s")
        f.metadata("Finish Reason", choice.get("finish_reason", "unknown") if "choice" in locals() else "unknown")
        f.print()

        return {
            "model": model_name,
            "description": description,
            "tokens": total_tokens,
            "total_time": total_time,
            "tokens_per_sec": tps,
            "ttft": ttft,
            "avg_itl": total_time / total_tokens if total_tokens > 0 else 0,
            "finish_reason": choice.get("finish_reason", "unknown") if "choice" in locals() else "unknown",
            "response": generated_text[:200],  # First 200 chars
        }

    except Exception as e:
        f.error(f"{type(e).__name__}: {e}")
        f.print()
        return None


def main():
    """Main entry point - test multiple models."""
    f = Formatter(show_raw=True)

    f.header("STAGE 1 EXERCISE 4: EXPLORE DIFFERENT MODELS")
    f.script("Comparing Token Speeds and Response Quality")
    f.print()

    # Load configuration
    base_url = config.api_base
    api_key = config.api_key

    # Get models to test - use command-line args if provided, otherwise defaults
    if len(sys.argv) > 1:
        # Parse command-line arguments as model names
        models_to_test = {}
        for arg in sys.argv[1:]:
            models_to_test[arg] = f"Custom: {arg}"
    else:
        models_to_test = DEFAULT_MODELS

    f.config(f"  Base URL: {base_url}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    f.script("Models to test:")
    for name, desc in models_to_test.items():
        f.script(f"  - {name}: {desc}")
    f.print()

    # Test prompt - same for all models
    test_prompt = "Explain the difference between synchronous and asynchronous programming in 2-3 sentences."

    # Results table header
    f.subheader("PERFORMANCE COMPARISON TABLE")
    f.print()
    f.dim(f"  {'Model':<20} {'Tokens':<10} {'Time(s)':<10} {'Tok/Sec':<10} {'TTFT(s)':<10}")
    f.dim("  " + "-" * 60)
    f.print()

    results = []

    # Create client for each model
    for model_name, description in models_to_test.items():
        # Skip 'default' if it's just a placeholder
        if model_name == "default":
            model_name = config.model

        client = APIClient(
            base_url=base_url,
            model=model_name,
            api_key=api_key,
        )

        result = test_model(f, model_name, description, client, test_prompt)
        if result:
            results.append(result)
            f.script(f"  {result['model']:<20} {result['tokens']:<10} {result['total_time']:<10.2f} {result['tokens_per_sec']:<10.2f} {result['ttft']:<10.2f}")
            f.print()

    f.print()

    # Summary comparison
    if results:
        f.subheader("MODEL COMPARISON SUMMARY")
        f.print()

        # Find best model for each metric
        fastest_tps = max(results, key=lambda r: r["tokens_per_sec"])
        fastest_ttft = min(results, key=lambda r: r["ttft"])
        most_tokens = max(results, key=lambda r: r["tokens"])

        f.script("  Best by Metric:")
        f.script(f"    Fastest Tokens/Sec:    {fastest_tps['model']} ({fastest_tps['tokens_per_sec']:.2f} tok/s)")
        f.script(f"    Lowest TTFT:           {fastest_ttft['model']} ({fastest_ttft['ttft']:.2f}s)")
        f.script(f"    Most Tokens Generated: {most_tokens['model']} ({most_tokens['tokens']} tokens)")
        f.print()

        # Quality observation notes
        f.subheader("RESPONSE QUALITY OBSERVATIONS")
        f.print()
        for result in results:
            f.script(f"  {result['model']}:")
            f.script(f"    Response: {result['response'][:150]}...")
            f.print()

        f.subheader("TIPS FOR OBSERVATION")
        f.script("  - Faster models (higher tok/s) are better for real-time apps")
        f.script("  - Lower TTFT means the first word appears quicker (better UX)")
        f.script("  - Response quality is subjective - compare coherence and accuracy")
        f.script("  - Some models excel at code, others at creative writing")
        f.script("  - Consider trade-offs: speed vs quality vs cost")
        f.print()


if __name__ == "__main__":
    main()