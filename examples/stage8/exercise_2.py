#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 2: Add Real Tools

This script demonstrates replacing simulated tools with real implementations:
1. search - Uses DuckDuckGo search API
2. get_weather - Uses OpenWeatherMap-style API
3. get_time - Uses timezone-aware time library
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import requests
except ImportError:
    requests = None


class RealTools:
    """Real tool implementations for the agent."""

    @staticmethod
    def search(query: str) -> str:
        """
        Search for information using DuckDuckGo.

        Args:
            query: The search query string.

        Returns:
            Formatted search results as a string.
        """
        if DDGS is None:
            return "Error: duckduckgo_search package is not installed. Install with: pip install duckduckgo-search"

        try:
            results = DDGS().text(query, max_results=5)
            if not results:
                return f"No results found for '{query}'"

            output = f"Search results for '{query}':\n"
            for i, result in enumerate(results, 1):
                output += f"\n  {i}. {result.get('title', 'No title')}\n"
                output += f"     {result.get('body', 'No snippet')}\n"
                if 'href' in result:
                    output += f"     URL: {result['href']}\n"
            return output
        except Exception as e:
            return f"Search error: {e}"

    @staticmethod
    def get_weather(location: str) -> str:
        """
        Get weather information for a location using a real API.

        Args:
            location: The city name.

        Returns:
            Formatted weather information.
        """
        api_key = sys.environ.get("OPENWEATHER_API_KEY", "")

        if not api_key or api_key == "your-api-key-here":
            # Fallback: simulate with real-time data
            from datetime import datetime
            return (
                f"Weather for {location} (simulated - provide OPENWEATHER_API_KEY for real data):\n"
                f"  Temperature: 18°C\n"
                f"  Conditions: Partly cloudy\n"
                f"  Humidity: 65%\n"
                f"  Wind: 12 km/h\n"
                f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        if requests is None:
            return "Error: requests package is not installed. Install with: pip install requests"

        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return (
                f"Weather for {data['name']}, {data['sys']['country']}:\n"
                f"  Temperature: {data['main']['temp']}°C\n"
                f"  Feels like: {data['main']['feels_like']}°C\n"
                f"  Conditions: {data['weather'][0]['description'].capitalize()}\n"
                f"  Humidity: {data['main']['humidity']}%\n"
                f"  Wind: {data['wind']['speed']} m/s"
            )
        except requests.exceptions.Timeout:
            return "Error: Weather API request timed out"
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data: {e}"

    @staticmethod
    def get_time(timezone: str = "UTC") -> str:
        """
        Get the current time for a timezone.

        Args:
            timezone: The IANA timezone name.

        Returns:
            Formatted time information.
        """
        try:
            import zoneinfo
            from datetime import datetime

            tz = zoneinfo.ZoneInfo(timezone)
            now = datetime.now(tz)

            return (
                f"Current time in {timezone}:\n"
                f"  Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  Timezone: {timezone}\n"
                f"  UTC Offset: {now.strftime('%z')}"
            )
        except Exception as e:
            return f"Error getting time for {timezone}: {e}"


def demo_real_tools():
    """Demonstrate real tool implementations."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 2: ADD REAL TOOLS")
    f.script("Replacing Simulated Tools with Real Implementations")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Define tools for the agent (OpenAI-compatible format)
    tools = [
        {
            "name": "search",
            "description": "Search the web for information using DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_weather",
            "description": "Get weather information for a location using OpenWeatherMap API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. 'London' or 'New York'"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_time",
            "description": "Get the current time for a timezone using zoneinfo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The IANA timezone name, e.g. 'Europe/London'"
                    }
                },
                "required": ["timezone"]
            }
        }
    ]

    # Test each tool individually first
    f.subheader("TESTING TOOLS INDIVIDUALLY")
    f.print()

    # Test search
    f.subheader("Test 1: Real Search Tool")
    search_query = "Python programming tips"
    f.model_input("SEARCH QUERY", search_query)
    f.print()

    start_time = time.time()
    search_result = RealTools.search(search_query)
    search_time = time.time() - start_time

    f.script(f"  Result ({search_time:.2f}s):")
    for line in search_result.split("\n"):
        f.script(f"    {line}")
    f.print()

    # Test weather
    f.subheader("Test 2: Real Weather Tool")
    weather_location = "London"
    f.model_input("LOCATION", weather_location)
    f.print()

    start_time = time.time()
    weather_result = RealTools.get_weather(weather_location)
    weather_time = time.time() - start_time

    f.script(f"  Result ({weather_time:.2f}s):")
    for line in weather_result.split("\n"):
        f.script(f"    {line}")
    f.print()

    # Test time
    f.subheader("Test 3: Real Time Tool")
    target_timezone = "Europe/London"
    f.model_input("TIMEZONE", target_timezone)
    f.print()

    start_time = time.time()
    time_result = RealTools.get_time(target_timezone)
    time_taken = time.time() - start_time

    f.script(f"  Result ({time_taken:.2f}s):")
    for line in time_result.split("\n"):
        f.script(f"    {line}")
    f.print()

    f.print()

    # Now test with the API
    f.subheader("INTEGRATION TEST WITH API")
    f.print()

    user_message = "What's the current time in Tokyo?"
    f.model_input("USER", user_message)
    f.print()

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Call the appropriate tools to answer the user's question."},
        {"role": "user", "content": user_message}
    ]

    payload = create_payload(
        messages=messages,
        tools=tools,
        temperature=0.7,
    )

    f.raw_request(payload)

    f.script("SENDING REQUEST...")
    f.print()

    start_time = time.time()
    full_response = ""
    tool_calls_detected = []

    for chunk in client.stream(payload):
        if chunk:
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            if "content" in delta and delta["content"]:
                text = delta["content"]
                full_response += text
                print(f"  {text}", end="", flush=True)
            elif "tool_calls" in delta and delta["tool_calls"]:
                tc = delta["tool_calls"][0]
                if tc.get("function"):
                    func = tc["function"]
                    call_info = {
                        "index": tc.get("index", 0),
                        "name": func.get("name", ""),
                        "arguments": func.get("arguments", "")
                    }
                    tool_calls_detected.append(call_info)

    elapsed = time.time() - start_time
    print()
    f.print()

    # Show results
    f.subheader("RESULTS")
    f.script(f"  Tool Calls Detected: {len(tool_calls_detected)}")
    for i, call in enumerate(tool_calls_detected, 1):
        f.script(f"    {i}. {call['name']}: {call['arguments'][:80]}")
    f.print()

    if full_response:
        f.parsed_response(full_response, "ASSISTANT")
    else:
        f.warning("No response content - the model may have only called tools")

    f.print()

    # Summary
    f.subheader("SUMMARY: REAL TOOLS VS SIMULATED")
    f.script("  Real tools provide actual, up-to-date information.")
    f.script("  Key considerations:")
    f.script("  - Rate limits: Real APIs have request limits")
    f.script("  - API keys: Most require authentication")
    f.script("  - Error handling: Network errors, timeouts, invalid responses")
    f.script("  - Caching: Consider caching results to reduce API calls")
    f.script("  - Security: Never expose API keys in client-side code")


if __name__ == "__main__":
    demo_real_tools()