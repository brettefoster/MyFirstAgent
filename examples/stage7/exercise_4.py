#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 4: Add Custom Tools

This script demonstrates how to extend the orchestrator with custom tools,
showing how to register new functionality and test it through natural language.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter

# Import orchestrator components
from stage7_orchestrator.orchestrator import Orchestrator, AgentConfig, AgentResponse
from stage5_sandboxed_hand.tool_registry import ToolRegistry


class CustomOrchestrator(Orchestrator):
    """Extended orchestrator with custom tools."""

    def _register_custom_tools(self) -> None:
        """Register custom tools for the agent."""

        @self.registry.register
        def get_quote() -> str:
            """Get a random inspirational quote."""
            quotes = [
                "The only way to do great work is to love what you do. - Steve Jobs",
                "Innovation distinguishes between a leader and a follower. - Steve Jobs",
                "Life is what happens when you're busy making other plans. - John Lennon",
                "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
                "It does not matter how slowly you go as long as you do not stop. - Confucius",
            ]
            import random
            return f"Quote: {random.choice(quotes)}"

        @self.registry.register
        def joke(category: str = "programming") -> str:
            """Tell a joke from a given category."""
            jokes = {
                "programming": [
                    "Why do programmers prefer dark mode? Because light attracts bugs.",
                    "A SQL query walks into a bar, sees two tables, and asks: 'Can I JOIN you?'",
                    "There are only 10 types of people: those who understand binary and those who don't.",
                ],
                "general": [
                    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
                    "What do you call a fake noodle? An impasta.",
                    "Why did the scarecrow win an award? Because he was outstanding in his field.",
                ],
            }
            available = jokes.get(category.lower(), jokes["programming"])
            import random
            return f"Joke ({category}): {random.choice(available)}"

        @self.registry.register
        def translate(text: str, target_language: str = "French") -> str:
            """Translate text to a target language (simulated)."""
            # Simulated translations (in a real agent, this would call a translation API)
            translations = {
                "French": {
                    "hello": "bonjour",
                    "goodbye": "au revoir",
                    "thank you": "merci",
                },
                "Spanish": {
                    "hello": "hola",
                    "goodbye": "adios",
                    "thank you": "gracias",
                },
                "German": {
                    "hello": "hallo",
                    "goodbye": "auf wiedersehen",
                    "thank you": "danke",
                },
            }
            lang_lower = target_language.lower()
            text_lower = text.lower().strip()

            if lang_lower in translations and text_lower in translations[lang_lower]:
                translated = translations[lang_lower][text_lower]
            else:
                translated = f"[Simulated {target_language} translation of: '{text}']"

            return f"{text} -> {target_language}: {translated}"

        @self.registry.register
        def fact(topic: str = "science") -> str:
            """Get an interesting fact about a topic."""
            facts = {
                "science": [
                    "Honey never spoils. Archaeologists have found 3,000-year-old honey that's still edible.",
                    "A group of flamingos is called a 'flamboyance'.",
                    "Octopuses have three hearts and blue blood.",
                ],
                "space": [
                    "A day on Venus is longer than its year.",
                    "There are more stars in the universe than grains of sand on Earth.",
                    "Neutron stars can spin at up to 600 rotations per second.",
                ],
                "history": [
                    "Cleopatra lived closer to the Moon landing than to the construction of the Great Pyramid.",
                    "The shortest war in history lasted 38 minutes (Britain vs Zanzibar, 1896).",
                    "Nelson Mandela was imprisoned 27 years before becoming president of South Africa.",
                ],
            }
            import random
            available = facts.get(topic.lower(), facts["science"])
            return f"Fact about {topic}: {random.choice(available)}"

    def run_with_custom_tools(self, user_message: str) -> AgentResponse:
        """Run with custom tools registered."""
        self._register_custom_tools()
        return self.run(user_message)


def demo_custom_tools():
    """Demonstrate custom tool registration and usage."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 4: ADD CUSTOM TOOLS")
    f.script("Extending the Orchestrator with New Functionality")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create custom orchestrator
    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    orchestrator = CustomOrchestrator(agent_config)

    # Show default tools
    f.subheader("DEFAULT TOOLS")
    default_tools = orchestrator.registry.get_tools()
    f.script(f"  Default tools ({len(default_tools)}):")
    for tool in default_tools:
        f.script(f"    - {tool['name']}: {tool['description']}")
    f.print()

    # Register custom tools
    f.script("Registering custom tools...")
    orchestrator._register_custom_tools()

    # Show all tools
    all_tools = orchestrator.registry.get_tools()
    f.subheader("ALL AVAILABLE TOOLS")
    f.script(f"  Total tools ({len(all_tools)}):")
    for tool in all_tools:
        f.script(f"    - {tool['name']}: {tool['description']}")
    f.print()

    # Show custom tool schemas
    f.subheader("CUSTOM TOOL SCHEMAS")
    custom_tool_names = ["get_quote", "joke", "translate", "fact"]
    for tool in all_tools:
        if tool["name"] in custom_tool_names:
            f.script(f"  {tool['name']}:")
            f.script(f"    Description: {tool['description']}")
            f.script(f"    Parameters: {json.dumps(tool['parameters'], indent=6)}")
            f.print()

    # Test custom tools through natural language queries
    f.subheader("TESTING CUSTOM TOOLS")
    f.script("  Queries designed to trigger custom tool usage:")
    f.print()

    queries = [
        "Give me an inspirational quote.",
        "Tell me a programming joke.",
        "Translate 'hello' to French.",
        "Give me an interesting fact about space.",
    ]

    for i, query in enumerate(queries, 1):
        f.subheader(f"QUERY {i}: \"{query}\"")
        f.model_input("USER", query)
        f.print()

        start_time = time.time()
        response: AgentResponse = orchestrator.run(query)
        elapsed = time.time() - start_time

        f.script(f"  Response: {response.content}")
        f.script(f"  Time: {elapsed:.2f}s")
        f.print()

        if response.tool_calls:
            f.subheader("TOOL CALLS MADE")
            for call in response.tool_calls:
                f.script(f"  Tool: {call.name}")
                f.script(f"    Arguments: {json.dumps(call.arguments, indent=6)}")
                # Find the tool result
                for result in response.tool_results:
                    if result["name"] == call.name:
                        f.script(f"    Result: {result['result']}")
            f.print()

        if i < len(queries):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next query...")
            f.print()
            time.sleep(2)

    # Summary
    f.subheader("HOW CUSTOM TOOL REGISTRATION WORKS")
    f.script("  1. Subclass Orchestrator and override _register_custom_tools()")
    f.script("  2. Use @self.registry.register decorator on methods")
    f.script("  3. The decorator extracts:")
    f.script("     - Function name -> tool name")
    f.script("     - Docstring -> tool description")
    f.script("     - Type hints -> JSON Schema parameters")
    f.script("  4. Tools are available to the model in subsequent API calls")
    f.script("  5. The model decides when to use them based on the query")
    f.print()

    f.subheader("KEY BENEFITS OF CUSTOM TOOLS")
    f.script("  - Extend agent capabilities without modifying core code")
    f.script("  - Type hints provide automatic schema generation")
    f.script("  - Docstrings become tool descriptions for the model")
    f.script("  - Tools can have optional parameters with defaults")


def demo_tool_registry_directly():
    """Demonstrate the ToolRegistry directly for deeper understanding."""
    f = Formatter(show_raw=True)

    f.header("TOOL REGISTRY DIRECT DEMO")
    f.script("Understanding the registry mechanism")
    f.print()

    registry = ToolRegistry()

    # Register tools using the decorator
    @registry.register
    def greet(name: str, formal: bool = False) -> str:
        """Greet a person by name."""
        if formal:
            return f"Good day, {name}. I trust this message finds you well."
        return f"Hey {name}! How's it going?"

    @registry.register
    def add(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    @registry.register
    def repeat(text: str, count: int = 3) -> str:
        """Repeat a text a specified number of times."""
        return " ".join([text] * count)

    # Show registered tools
    f.subheader("REGISTERED TOOLS")
    tools = registry.get_tools()
    for tool in tools:
        f.subheader(f"Tool: {tool['name']}")
        f.script(f"  Description: {tool['description']}")
        f.script(f"  Parameters: {json.dumps(tool['parameters'], indent=4)}")
        f.script(f"  Required: {tool['parameters'].get('required', [])}")
        f.print()

    # Execute some test calls
    f.subheader("EXECUTING TEST CALLS")
    test_calls = [
        {"name": "greet", "arguments": {"name": "Alice"}},
        {"name": "greet", "arguments": {"name": "Professor Smith", "formal": True}},
        {"name": "add", "arguments": {"a": 42, "b": 13}},
        {"name": "repeat", "arguments": {"text": "go", "count": 4}},
    ]

    for call_data in test_calls:
        from stage5_sandboxed_hand.tool_registry import ToolCall
        call = ToolCall(
            name=call_data["name"],
            arguments=call_data["arguments"]
        )
        result = registry.execute(call)
        f.script(f"  {call.name}({json.dumps(call.arguments)})")
        f.script(f"    -> {result.output} (success: {result.success})")
        f.print()


if __name__ == "__main__":
    # Run main demo
    demo_custom_tools()

    f = Formatter()
    f.subheader("OPTIONAL: REGISTRY DIRECT DEMO")
    f.script("  To see the ToolRegistry in action:")
    f.script("    python examples/stage7/exercise_4.py --registry")
    f.print()

    # Run registry demo if flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--registry":
        demo_tool_registry_directly()