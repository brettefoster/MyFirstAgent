#!/usr/bin/env python3
"""
Stage 1: The Raw Sensor

This script demonstrates how to communicate directly with an OpenAI-compatible
API using raw HTTP requests and Server-Sent Events (SSE) streaming, without
any SDK wrappers. Works with Ollama, vLLM, LocalAI, and other compatible servers.

Run with: python raw_stream.py
"""

import json
import time

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("STAGE 1: THE RAW SENSOR")
    print("Exposing Raw JSON Streams from OpenAI-Compatible API")
    print("=" * 60 + "\n")
    
    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key
    
    print(f"Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    print()
    
    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)
    
    # Example prompts
    prompts = [
        "Explain quantum computing in one sentence.",
        "What is the capital of France?",
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'#'*60}")
        print(f"# Prompt {i}: {prompt}")
        print(f"{'#'*60}\n")
        
        # Create OpenAI-compatible payload
        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        print("RAW PAYLOAD:")
        print(json.dumps(payload, indent=2))
        print(f"\n{'='*60}")
        print("RAW STREAM CHUNKS START")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        last_token_time = start_time
        
        # Stream response
        for chunk in client.stream(payload):
            if "_raw" in chunk:
                print(f"RAW: {chunk['_raw'][:100]}...")
                continue
            
            # Parse OpenAI-style response
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})
            
            if "content" in delta and delta["content"]:
                token = delta["content"]
                current_time = time.time()
                
                # Calculate timing
                ttft = current_time - start_time
                inter_token = current_time - last_token_time
                last_token_time = current_time
                
                print(f"PARSED TOKEN: {token}")
                print(f"TTFT: {ttft:.2f}s | Inter-Token: {inter_token:.3f}s")
                print("-" * 40)
            
            # Check for finish reason
            if "finish_reason" in choice and choice["finish_reason"]:
                print(f"\n>>> STREAM COMPLETE. Finish reason: {choice['finish_reason']}")
        
        print(f"\n{'='*60}")
        print("RAW STREAM CHUNKS END")
        print(f"{'='*60}\n")
        
        if i < len(prompts):
            print("\n" + "-" * 60)
            print("Waiting 2 seconds before next request...")
            time.sleep(2)


if __name__ == "__main__":
    main()
