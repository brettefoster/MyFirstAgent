#!/usr/bin/env python3
"""
Generic OpenAI-Compatible API Client

This module provides a unified interface for streaming from any OpenAI-compatible
API endpoint (e.g., Ollama, vLLM, LocalAI, Groq, etc.).

Run with: python -m utils.api_client
"""

import json
import time
from typing import Dict, Any, List, Optional, Generator
from urllib import request
from urllib.error import URLError, HTTPError

# Import central configuration for default values
from utils.config import config


class APIClient:
    """
    A generic client for OpenAI-compatible API endpoints.
    
    This client works with any API that follows the OpenAI chat completion format,
    including local deployments like Ollama, vLLM, and other compatible servers.
    
    Example:
        client = APIClient(base_url="http://localhost:11434", model="llama3")
        for chunk in client.stream({"messages": [{"role": "user", "content": "Hello"}]}):
            print(chunk)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        api_key: str = "ollama"  # Default for Ollama (usually not needed)
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: The base URL of the OpenAI-compatible API.
            model: The model to use for completions.
            api_key: The API key (often not needed for local deployments).
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self._stream_url = f"{self.base_url}/v1/chat/completions"
    
    def stream(
        self,
        payload: Dict[str, Any],
        stream: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a request to the API and yield parsed JSON chunks.
        
        Args:
            payload: The request payload (should contain 'messages').
            stream: Whether to stream the response.
            
        Yields:
            Parsed JSON dictionaries from each SSE data line.
        """
        # Merge model into payload if not already present
        payload["model"] = payload.get("model", self.model)
        payload["stream"] = stream
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key and self.api_key != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = json.dumps(payload).encode("utf-8")
        
        try:
            req = request.Request(
                self._stream_url,
                data=data,
                headers=headers,
                method="POST"
            )
            
            with request.urlopen(req, timeout=120) as response:
                for line in response:
                    decoded_line = line.decode("utf-8").strip()
                    
                    if not decoded_line:
                        continue
                    
                    # SSE format: each line starts with "data: "
                    if decoded_line.startswith("data:"):
                        json_data = decoded_line[5:].strip()
                        
                        if json_data in ("[DONE]", ""):
                            continue
                        
                        try:
                            yield json.loads(json_data)
                        except json.JSONDecodeError:
                            yield {"_raw": decoded_line}
        
        except HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"HTTP Error {e.code}: {e.reason} - {error_body}") from e
        except URLError as e:
            raise RuntimeError(f"URL Error: {e.reason}") from e
    
    def request(
        self,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Make a non-streaming request to the API and return the full response.

        Args:
            payload: The request payload (should contain 'messages').

        Returns:
            The parsed JSON response dictionary, or None on failure.
        """
        # Ensure stream is explicitly False for non-streaming
        payload["model"] = payload.get("model", self.model)
        payload["stream"] = False

        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key and self.api_key != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = json.dumps(payload).encode("utf-8")

        try:
            req = request.Request(
                self._stream_url,
                data=data,
                headers=headers,
                method="POST"
            )

            with request.urlopen(req, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"HTTP Error {e.code}: {e.reason} - {error_body}")
            return None
        except URLError as e:
            print(f"URL Error: {e.reason}")
            return None

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat completion request.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            tools: Optional list of tool/function definitions.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate (defaults to config.max_tokens).
            
        Yields:
            Parsed JSON chunks from the stream.
        """
        if max_tokens is None:
            max_tokens = config.max_tokens

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        yield from self.stream(payload)


def format_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format tools for OpenAI-compatible API.
    
    Args:
        tools: List of tool definitions.
        
    Returns:
        Formatted tools in OpenAI function calling format.
    """
    formatted = []
    for tool in tools:
        formatted.append({
            "type": "function",
            "function": {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {})
            }
        })
    return formatted


def create_payload(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a request payload for OpenAI-compatible API.
    
    Args:
        messages: List of message dictionaries.
        tools: Optional list of tool definitions.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate (defaults to config.max_tokens).
        model: Model name (overrides default).
        
    Returns:
        Request payload dictionary.
    """
    if max_tokens is None:
        max_tokens = config.max_tokens

    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if model:
        payload["model"] = model
    
    if tools:
        payload["tools"] = format_tools(tools)
        payload["tool_choice"] = "auto"
    
    return payload


def demo_client():
    """Demonstrate the API client."""
    from utils.config import config

    base_url = config.api_base
    model = config.model
    api_key = config.api_key
    
    print("\n" + "=" * 60)
    print("GENERIC API CLIENT DEMO")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print("=" * 60 + "\n")
    
    client = APIClient(base_url=base_url, model=model, api_key=api_key)
    
    messages = [
        {"role": "user", "content": "Hello! What can you do?"}
    ]
    
    print("Streaming response...\n")
    
    for chunk in client.chat(messages):
        if "_raw" in chunk:
            print(f"RAW: {chunk['_raw'][:100]}...")
            continue
        
        choice = chunk.get("choices", [{}])[0]
        delta = choice.get("delta", {})
        
        if "content" in delta and delta["content"]:
            print(delta["content"], end="", flush=True)
        elif "reasoning_content" in delta and delta["reasoning_content"]:
            # Handle reasoning/thinking content (e.g., from models with CoT)
            print(f"[{delta['reasoning_content']}]", end="", flush=True)
        elif "tool_calls" in delta and delta["tool_calls"]:
            print(f"\n[TOOL CALL: {delta['tool_calls']}]")
    
    print("\n\nDone!")


if __name__ == "__main__":
    demo_client()