#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 6: Tool Output Formatting

This script demonstrates building formatters that make tool output
LLM-friendly, with clear structure and consistent formatting.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage5_sandboxed_hand.tool_registry import ToolRegistry, ToolCall, ToolResult


def format_tool_output(tool_name: str, result: str, success: bool) -> str:
    """
    Format tool output for the LLM.
    
    This is a simple formatter that produces a clear, consistent output
    format that LLMs can easily parse.
    
    Args:
        tool_name: The name of the tool that was executed.
        result: The output/result string from the tool.
        success: Whether the tool execution was successful.
        
    Returns:
        Formatted string for LLM consumption.
    """
    if success:
        return f"[TOOL: {tool_name}] Success: {result}"
    else:
        return f"[TOOL: {tool_name}] Error: {result}"


def format_tool_output_detailed(tool_name: str, result: str, success: bool, 
                                 execution_time: float = 0, token_count: int = 0) -> str:
    """
    Format tool output with additional metadata for the LLM.
    
    Args:
        tool_name: The name of the tool.
        result: The tool output.
        success: Whether execution succeeded.
        execution_time: Time taken to execute (in seconds).
        token_count: Estimated token count of the output.
        
    Returns:
        Detailed formatted string with metadata.
    """
    status = "SUCCESS" if success else "ERROR"
    
    lines = [
        f"=== TOOL EXECUTION ===",
        f"Tool: {tool_name}",
        f"Status: {status}",
    ]
    
    if success:
        lines.append(f"Output:\n{result}")
    else:
        lines.append(f"Error: {result}")
    
    if execution_time > 0:
        lines.append(f"Execution Time: {execution_time:.3f}s")
    
    if token_count > 0:
        lines.append(f"Output Tokens: ~{token_count}")
    
    lines.append(f"=== END TOOL EXECUTION ===")
    
    return "\n".join(lines)


def format_tool_output_json(tool_name: str, result: str, success: bool,
                             **kwargs) -> str:
    """
    Format tool output as structured JSON for machine parsing.
    
    Args:
        tool_name: The name of the tool.
        result: The tool output.
        success: Whether execution succeeded.
        **kwargs: Additional fields to include in the output.
        
    Returns:
        JSON string with tool execution details.
    """
    output = {
        "tool": tool_name,
        "success": success,
        "output": result if success else None,
        "error": None if success else result,
    }
    output.update(kwargs)
    
    return json.dumps(output, indent=2)


def estimate_token_count(text: str) -> int:
    """
    Rough estimate of token count for a text string.
    
    This is a simplified estimation - actual token counts depend on
    the specific tokenizer used by the model.
    
    Args:
        text: The text to estimate tokens for.
        
    Returns:
        Estimated number of tokens.
    """
    # Rough estimate: ~4 characters per token for English text
    return max(1, len(text) // 4)


def demo_output_formatting():
    """Demonstrate different tool output formatting styles."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 6: TOOL OUTPUT FORMATTING")
    f.script("Making Tool Output LLM-Friendly")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create registry with sample tools
    registry = ToolRegistry()

    @registry.register
    def search(query: str) -> str:
        """Search for information on the web."""
        return (
            f"Search results for '{query}':\n"
            "1. https://example.com/article1 - Relevant information about the topic\n"
            "2. https://example.com/article2 - Detailed explanation with examples\n"
            "3. https://example.com/article3 - Community discussion and insights"
        )

    @registry.register
    def calculate(expression: str) -> str:
        """Perform a mathematical calculation."""
        from stage5_sandboxed_hand.tool_registry import safe_eval
        try:
            result = safe_eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error: {e}"

    @registry.register
    def get_weather(location: str) -> str:
        """Get weather information for a location."""
        return (
            f"Weather in {location}:\n"
            "  Temperature: 18°C (64°F)\n"
            "  Conditions: Partly cloudy\n"
            "  Humidity: 65%\n"
            "  Wind: 12 km/h NW\n"
            "  Forecast: Chance of rain 20% this evening"
        )

    # Get tool schemas
    tools = registry.get_tools()
    tool_schemas = {tool["name"]: tool for tool in tools}

    # Test tool calls
    test_calls = [
        ToolCall(name="search", arguments={"query": "machine learning basics"}),
        ToolCall(name="calculate", arguments={"expression": "2**10 + 100"}),
        ToolCall(name="get_weather", arguments={"location": "San Francisco"}),
        ToolCall(name="search", arguments={"query": "python tutorials"}),
    ]

    # Format 1: Simple format
    f.subheader("FORMAT 1: SIMPLE FORMAT")
    f.script("  Format: [TOOL: name] Success/Error: result")
    f.print()

    for tool_call in test_calls:
        result = registry.execute(tool_call)
        formatted = format_tool_output(
            tool_call.name,
            result.output if result.success else result.error or "",
            result.success
        )
        f.script(formatted)
        f.print()

    # Format 2: Detailed format
    f.subheader("FORMAT 2: DETAILED FORMAT WITH METADATA")
    f.script("  Format: Structured block with tool name, status, output, timing")
    f.print()

    import time
    for tool_call in test_calls:
        start = time.time()
        result = registry.execute(tool_call)
        elapsed = time.time() - start
        
        output_text = result.output if result.success else (result.error or "No output")
        formatted = format_tool_output_detailed(
            tool_call.name,
            output_text,
            result.success,
            execution_time=elapsed,
            token_count=estimate_token_count(output_text)
        )
        f.script(formatted)
        f.print()

    # Format 3: JSON format
    f.subheader("FORMAT 3: JSON FORMAT (MACHINE-PARSABLE)")
    f.script("  Format: Structured JSON for programmatic parsing")
    f.print()

    for tool_call in test_calls:
        result = registry.execute(tool_call)
        output_text = result.output if result.success else (result.error or "No output")
        formatted = format_tool_output_json(
            tool_call.name,
            output_text,
            result.success,
            tool_call=tool_call.name,
            arguments=tool_call.arguments
        )
        f.raw_response(json.loads(formatted))
        f.print()

    # Comparison
    f.subheader("FORMAT COMPARISON")
    f.script("  Simple Format:")
    f.script("    + Easy for LLMs to parse")
    f.script("    + Compact output")
    f.script("    - Limited metadata")
    f.script("    - Harder to extract structured data")
    f.print()
    f.script("  Detailed Format:")
    f.script("    + Rich metadata (timing, token count)")
    f.script("    + Clear section boundaries")
    f.script("    - More verbose")
    f.script("    - May use more tokens")
    f.print()
    f.script("  JSON Format:")
    f.script("    + Machine-parsable")
    f.script("    + Structured and extensible")
    f.script("    + Easy to add new fields")
    f.script("    - Less human-readable")
    f.script("    - May need post-processing for LLM consumption")
    f.print()

    # Token cost analysis
    f.subheader("TOKEN COST ANALYSIS")
    f.script("  Comparing output sizes for a sample tool result:")
    f.print()

    sample_output = (
        "Search results for 'machine learning':\n"
        "1. https://example.com/ml-intro - Introduction to ML\n"
        "2. https://example.com/ml-algorithms - Common algorithms\n"
        "3. https://example.com/ml-tutorials - Learning resources"
    )

    formats = [
        ("Simple", format_tool_output("search", sample_output, True)),
        ("Detailed", format_tool_output_detailed("search", sample_output, True, 0.123, len(sample_output) // 4)),
        ("JSON", format_tool_output_json("search", sample_output, True)),
    ]

    f.script(f"  {'Format':<12} {'Chars':<10} {'Est. Tokens':<15}")
    f.script(f"  {'-' * 12} {'-' * 10} {'-' * 15}")
    for name, text in formats:
        chars = len(text)
        tokens = estimate_token_count(text)
        f.script(f"  {name:<12} {chars:<10,} {tokens:<15,}")

    f.print()
    f.script("  Note: Token estimation is approximate. Actual counts depend on the model's tokenizer.")


if __name__ == "__main__":
    demo_output_formatting()