#!/usr/bin/env python3
"""
Stage 1: The Raw Sensor

This script demonstrates how to communicate directly with the Gemini API
using raw HTTP requests and Server-Sent Events (SSE) streaming, without
any SDK wrappers.

Run with: python raw_stream.py
"""

import json
import time
from urllib import request
from urllib.error import URLError, HTTPError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-09-2025")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please set it in your .env file "
        "or as an environment variable."
    )

# Streaming endpoint URL
STREAM_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:streamGenerateContent?key={API_KEY}"
)


def create_payload(prompt: str) -> dict:
    """Create the request payload for the Gemini API."""
    return {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]
    }


class GeminiStream:
    """
    A reusable class for streaming responses from the Gemini API.
    
    This class wraps the raw HTTP streaming logic, making it easy to
    integrate with other stages of the agent.
    """
    
    def __init__(self, api_key: str, model: str = None):
        """
        Initialize the Gemini stream client.
        
        Args:
            api_key: The Gemini API key.
            model: The model to use. Defaults to the env var or a default.
        """
        self.api_key = api_key
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-09-2025")
        self._stream_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:streamGenerateContent?key={self.api_key}"
        )
    
    def stream(self, payload: dict):
        """
        Stream a request to the Gemini API and yield parsed JSON chunks.
        
        Args:
            payload: The request payload (should contain 'contents').
            
        Yields:
            Parsed JSON dictionaries from each SSE data line.
        """
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload).encode("utf-8")
        
        try:
            with request.Request(self._stream_url, data=data, headers=headers) as req:
                with request.urlopen(req) as response:
                    for line in response:
                        decoded_line = line.decode("utf-8").strip()
                        
                        if not decoded_line:
                            continue
                        
                        if decoded_line.startswith("data:"):
                            json_data = decoded_line[5:].strip()
                            
                            if json_data in ("[DONE]", ""):
                                continue
                            
                            try:
                                yield json.loads(json_data)
                            except json.JSONDecodeError:
                                # Yield raw line for debugging
                                yield {"_raw": decoded_line}
        
        except HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"HTTP Error {e.code}: {e.reason} - {error_body}") from e
        except URLError as e:
            raise RuntimeError(f"URL Error: {e.reason}") from e


def stream_response(payload: dict) -> None:
    """
    Send a streaming request to the Gemini API and parse the SSE response.
    
    The response comes as Server-Sent Events (SSE) where each line is prefixed
    with "data: " followed by a JSON object.
    """
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    
    print(f"{'='*60}")
    print(f"SENDING REQUEST TO: {STREAM_URL}")
    print(f"{'='*60}\n")
    
    print("RAW PAYLOAD:")
    print(json.dumps(payload, indent=2))
    print(f"\n{'='*60}")
    print("RAW STREAM CHUNKS START")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    last_token_time = start_time
    
    try:
        with request.Request(STREAM_URL, data=data, headers=headers) as req:
            with request.urlopen(req) as response:
                # Read the stream line by line
                for line in response:
                    decoded_line = line.decode("utf-8").strip()
                    
                    if not decoded_line:
                        continue
                    
                    # SSE format: each line starts with "data: "
                    if decoded_line.startswith("data:"):
                        # Extract the JSON part
                        json_data = decoded_line[5:].strip()
                        
                        # Skip empty data or done markers
                        if json_data in ("[DONE]", ""):
                            continue
                        
                        try:
                            data_json = json.loads(json_data)
                            
                            # Extract the token from the nested structure
                            candidates = data_json.get("candidates", [])
                            if candidates:
                                content = candidates[0].get("content", {})
                                parts = content.get("parts", [])
                                if parts:
                                    token = parts[0].get("text", "")
                                    current_time = time.time()
                                    
                                    # Calculate timing
                                    ttft = current_time - start_time
                                    inter_token = current_time - last_token_time
                                    last_token_time = current_time
                                    
                                    print(f"RAW CHUNK: {decoded_line[:100]}...")
                                    print(f"PARSED TOKEN: {token}")
                                    print(f"TTFT: {ttft:.2f}s | Inter-Token: {inter_token:.3f}s")
                                    print("-" * 40)
                            
                            # Check for finish reason
                            if "candidates" in data_json:
                                finish_reason = data_json["candidates"][0].get("finishReason")
                                if finish_reason:
                                    print(f"\n>>> STREAM COMPLETE. Finish reason: {finish_reason}")
                                    
                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error: {e}")
                            print(f"Raw line: {decoded_line}")
    
    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        error_body = e.read().decode("utf-8")
        print(f"Response: {error_body}")
    except URLError as e:
        print(f"URL Error: {e.reason}")


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("STAGE 1: THE RAW SENSOR")
    print("Exposing Raw JSON Streams from Gemini API")
    print("=" * 60 + "\n")
    
    # Example prompts
    prompts = [
        "Explain quantum computing in one sentence.",
        "What is the capital of France?",
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'#'*60}")
        print(f"# Prompt {i}: {prompt}")
        print(f"{'#'*60}\n")
        
        payload = create_payload(prompt)
        stream_response(payload)
        
        if i < len(prompts):
            print("\n" + "-" * 60)
            print("Waiting 2 seconds before next request...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print("RAW STREAM CHUNKS END")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()