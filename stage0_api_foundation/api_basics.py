#!/usr/bin/env python3
"""
Stage 0: The API Foundation

This script demonstrates how to make basic non-streaming API calls
to an OpenAI-compatible endpoint. It shows the complete request/response
cycle before introducing streaming complexity.

Run with: python api_basics.py
"""

import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the generic API client
from utils.api_client import APIClient, create_payload


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("STAGE 0: THE API FOUNDATION")
    print("Understanding Basic Request/Response")
    print("=" * 60 + "\n")
    
    # Load configuration
    base_url = os.getenv("API_BASE", "http://localhost:11434")
    model = os.getenv("MODEL", "llama3")
    api_key = os.getenv("API_KEY", "ollama")
    
    print(f"Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    print()
    
    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)
    
    # Example prompts
    prompts = [
        "What is machine learning?",
        "Explain the difference between supervised and unsupervised learning.",
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'#'*60}")
        print(f"# Prompt {i}: {prompt}")
        print(f"{'#'*60}\n")
        
        # Create OpenAI-compatible payload (non-streaming)
        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512,
            stream=False  # Important: non-streaming for Stage 0
        )
        
        print("REQUEST PAYLOAD:")
        print(json.dumps(payload, indent=2))
        print(f"\n{'='*60}")
        print("SENDING REQUEST...")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Make non-streaming request
        response = client.request(payload)  # Single request, not stream
        
        elapsed_time = time.time() - start_time
        
        if response is None:
            print("ERROR: Request failed!")
            continue
        
        # Parse the response
        print("RAW RESPONSE:")
        print(json.dumps(response, indent=2))
        
        # Extract key information
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        finish_reason = choice.get("finish_reason", "unknown")
        
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        print(f"\n{'='*60}")
        print("PARSED RESPONSE:")
        print(f"{'='*60}\n")
        
        print(f"ASSISTANT: {content}")
        print(f"\n{'-'*40}")
        print("METADATA:")
        print(f"  Finish Reason: {finish_reason}")
        print(f"  Prompt Tokens: {prompt_tokens}")
        print(f"  Completion Tokens: {completion_tokens}")
        print(f"  Total Tokens: {total_tokens}")
        print(f"  Response Time: {elapsed_time:.2f}s")
        
        # Explain finish reasons
        print(f"\n{'-'*40}")
        print("FINISH REASON EXPLANATION:")
        finish_explanations = {
            "stop": "The model reached a natural stopping point (end of sentence/paragraph).",
            "length": "The model hit the max_tokens limit and stopped.",
            "content_filter": "The response was filtered due to safety policies.",
            "function_call": "The model requested to call a function (tool).",
            "unknown": "Unknown or no finish reason provided."
        }
        explanation = finish_explanations.get(finish_reason, "Unknown reason.")
        print(f"  {explanation}")
        
        if i < len(prompts):
            print("\n" + "-" * 60)
            print("Waiting 2 seconds before next request...")
            time.sleep(2)


def demo_system_prompt():
    """Demonstrate the effect of system prompts."""
    print("\n" + "=" * 60)
    print("DEMO: SYSTEM PROMPT EFFECTS")
    print("=" * 60 + "\n")
    
    base_url = os.getenv("API_BASE", "http://localhost:11434")
    model = os.getenv("MODEL", "llama3")
    api_key = os.getenv("API_KEY", "ollama")
    
    client = APIClient(base_url=base_url, model=model, api_key=api_key)
    
    user_message = "What is 2 + 2?"
    
    # Without system prompt
    print("WITHOUT SYSTEM PROMPT:")
    print("-" * 40)
    payload1 = create_payload(
        messages=[{"role": "user", "content": user_message}],
        temperature=0.7,
        max_tokens=100
    )
    response1 = client.request(payload1)
    if response1:
        content1 = response1.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"Response: {content1}")
    
    # With system prompt
    print("\nWITH SYSTEM PROMPT ('You are a sarcastic robot'):")
    print("-" * 40)
    payload2 = create_payload(
        messages=[
            {"role": "system", "content": "You are a sarcastic robot who thinks humans are silly for asking simple questions."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=100
    )
    response2 = client.request(payload2)
    if response2:
        content2 = response2.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"Response: {content2}")
    
    print("\nNotice how the system prompt changes the tone and style!")


def demo_temperature():
    """Demonstrate the effect of temperature."""
    print("\n" + "=" * 60)
    print("DEMO: TEMPERATURE EFFECTS")
    print("=" * 60 + "\n")
    
    base_url = os.getenv("API_BASE", "http://localhost:11434")
    model = os.getenv("MODEL", "llama3")
    api_key = os.getenv("API_KEY", "ollama")
    
    client = APIClient(base_url=base_url, model=model, api_key=api_key)
    
    prompt = "Give me a creative story opening."
    
    for temp in [0.1, 0.7, 1.5]:
        print(f"\nTemperature: {temp}")
        print("-" * 40)
        
        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=50
        )
        
        response = client.request(payload)
        if response:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Response: {content}")


if __name__ == "__main__":
    main()
    demo_system_prompt()
    demo_temperature()