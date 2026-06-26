#!/usr/bin/env python3
"""
Output formatter with ANSI colors for distinguishing between
script output, model input, model output, and raw JSON responses.
"""

import json
import os
import re
from enum import Enum
from typing import Any, Optional


class Color(Enum):
    """ANSI color codes for terminal output."""
    # Basic colors
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"

    # Bright/bold colors
    BRIGHT_BLACK = "\033[0;90m"
    BRIGHT_RED = "\033[0;91m"
    BRIGHT_GREEN = "\033[0;92m"
    BRIGHT_YELLOW = "\033[0;93m"
    BRIGHT_BLUE = "\033[0;94m"
    BRIGHT_MAGENTA = "\033[0;95m"
    BRIGHT_CYAN = "\033[0;96m"
    BRIGHT_WHITE = "\033[0;97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    REVERSE = "\033[7m"
    RESET = "\033[0m"


# Global setting: respect NO_COLOR environment variable (convention)
_COLORS_ENABLED = not os.environ.get("NO_COLOR", "")


def colors_enabled() -> bool:
    """Check if colors are enabled."""
    return _COLORS_ENABLED


def set_colors_enabled(enabled: bool) -> None:
    """Enable or disable colors globally."""
    global _COLORS_ENABLED
    _COLORS_ENABLED = enabled


def _wrap(text: str, *colors: Color) -> str:
    """Wrap text with one or more ANSI color codes, respecting the colors enabled setting.
    
    Args:
        text: The text to wrap.
        *colors: One or more Color enums to apply (applied in order).
    """
    if _COLORS_ENABLED:
        prefix = "".join(c.value for c in colors)
        return f"{prefix}{text}{Color.RESET.value}"
    return text


# ─── High-level formatting functions ───────────────────────────────────


def header(title: str, width: int = 60) -> str:
    """Format a section header."""
    line = "=" * width
    return _wrap(f"\n{line}\n{title}\n{line}\n", Color.BOLD)


def subheader(title: str, width: int = 60) -> str:
    """Format a sub-section header."""
    line = "-" * width
    return _wrap(f"\n{line}\n{title}\n{line}\n", Color.BRIGHT_CYAN)


def script(text: str) -> str:
    """Format script/narrative output (white, normal)."""
    return _wrap(text, Color.WHITE)


def config(text: str) -> str:
    """Format configuration info (dim white)."""
    return _wrap(text, Color.BRIGHT_BLACK)


def model_input(label: str, content: str) -> str:
    """Format model input (e.g., user prompt, system prompt)."""
    label_part = _wrap(f"{label}: ", Color.BRIGHT_GREEN)
    content_part = _wrap(content, Color.GREEN)
    return f"{label_part}\n{content_part}"


def model_output(content: str, label: str = "ASSISTANT") -> str:
    """Format model output (e.g., assistant response)."""
    label_part = _wrap(f"{label}: ", Color.BRIGHT_MAGENTA)
    content_part = _wrap(content, Color.MAGENTA)
    return f"{label_part}\n{content_part}"


def parsed_response(content: str, label: str = "ASSISTANT", width: int = 60) -> str:
    """Format a parsed model response with a centered subheader separator.
    
    This ensures consistent formatting across all examples - the 'PARSED RESPONSE'
    separator is always included.
    """
    header_part = subheader("PARSED RESPONSE", width)
    label_part = _wrap(f"{label}: ", Color.BRIGHT_MAGENTA)
    content_part = _wrap(content, Color.MAGENTA)
    return f"{header_part}{label_part}\n{content_part}"


def metadata(label: str, value: str) -> str:
    """Format metadata key-value pairs (cyan)."""
    return _wrap(f"  {label}: {value}", Color.CYAN)


def _colorize_json_key(match: re.Match) -> str:
    """
    Colorize a JSON key (property name) in a JSON string.
    Matches patterns like "key": or , "key":
    Uses magenta for keys to make them stand out.
    """
    prefix = match.group(1)  # leading whitespace and optional comma
    key = match.group(2)     # the key string (with quotes)
    return f"{prefix}{_wrap(key, Color.BRIGHT_MAGENTA)}"


def _colorize_json_string(match: re.Match) -> str:
    """
    Colorize a JSON string value (not keys).
    Uses green for string values.
    """
    return _wrap(match.group(0), Color.GREEN)


def _colorize_json_numbers(match: re.Match) -> str:
    """
    Colorize JSON numbers.
    Uses yellow for numeric values.
    """
    return _wrap(match.group(0), Color.BRIGHT_YELLOW)


def _colorize_json_bool(match: re.Match) -> str:
    """
    Colorize JSON booleans (true/false).
    Uses cyan.
    """
    return _wrap(match.group(0), Color.CYAN)


def _colorize_json_null(match: re.Match) -> str:
    """
    Colorize JSON null.
    Uses bright black (dim).
    """
    return _wrap(match.group(0), Color.BRIGHT_BLACK)


def _highlight_json(json_str: str, highlight_keys: bool = True, highlight_reasoning: bool = True) -> str:
    """
    Apply ANSI color codes to a JSON string for better readability.
    
    Coloring scheme:
    - JSON keys (object property names): BRIGHT_MAGENTA (if highlight_keys is True)
    - String values: GREEN
    - Numbers: BRIGHT_YELLOW
    - Booleans: CYAN
    - null: BRIGHT_BLACK
    - Reasoning delimiters: colored inline inside string values when detected
    
    Args:
        json_str: The pretty-printed JSON string to colorize.
        highlight_keys: Whether to highlight JSON object keys. Defaults to True.
        highlight_reasoning: Whether to highlight reasoning delimiters in JSON string values. Defaults to True.
    
    Returns:
        The JSON string with ANSI color codes applied.
    """
    result = json_str
    
    if highlight_keys:
        # Highlight JSON object keys (strings followed by colon)
        # Pattern matches: optional whitespace + optional comma + whitespace + "key" + whitespace + :
        result = re.sub(
            r'((?:^|\s)(?:,\s*)?)("([^"]*?)")(\s*:\s*)',
            lambda m: f"{m.group(1)}{_wrap(m.group(2), Color.BRIGHT_MAGENTA)}{m.group(4)}",
            result,
            flags=re.MULTILINE
        )
    
    # Highlight JSON string values (but not keys - keys are already colored)
    # This is tricky because we need to avoid re-coloring already-colored keys.
    # We use a simpler approach: color string values that are NOT followed by a colon
    # (since keys are followed by colons)
    # Note: This is a best-effort approach and may not handle all edge cases perfectly
    
    # Highlight numbers (integers and floats, but not inside already-colored segments)
    # Match numbers that are values (not part of a key)
    result = re.sub(
        r'(?<=:\s)(-?\d+\.?\d*(?:[eE][+-]?\d+)?)',
        lambda m: _wrap(m.group(0), Color.BRIGHT_YELLOW),
        result
    )
    
    # Highlight booleans
    result = re.sub(
        r'(?<=:\s)(true|false)(?=\s*$|[\s,}\]])',
        lambda m: _wrap(m.group(0), Color.CYAN),
        result,
        flags=re.MULTILINE
    )
    
    # Highlight null
    result = re.sub(
        r'(?<=:\s)null(?=\s*$|[\s,}\]])',
        lambda m: _wrap(m.group(0), Color.BRIGHT_BLACK),
        result,
        flags=re.MULTILINE
    )
    
    if highlight_reasoning:
        result = _highlight_reasoning(result)

    return result


def raw_json(data: Any, label: str = "RAW RESPONSE", highlight_keys: bool = True, highlight_reasoning: bool = True) -> str:
    """
    Format raw JSON data with a colored label.
    The JSON keys and values are colorized for better readability:
    - Keys (object property names): BRIGHT_MAGENTA
    - String values: GREEN
    - Numbers: BRIGHT_YELLOW
    - Booleans: CYAN
    - null: BRIGHT_BLACK
    
    Args:
        data: The JSON-serializable data to format.
        label: The label to display above the JSON.
        highlight_keys: Whether to highlight JSON object keys. Defaults to True.
    """
    sep = _wrap("-" * 60, Color.DIM)
    header_line = _wrap(f"{sep}\n{label}\n{sep}", Color.BRIGHT_YELLOW)
    json_str = json.dumps(data, indent=2)
    highlighted_json = _highlight_json(
        json_str,
        highlight_keys=highlight_keys,
        highlight_reasoning=highlight_reasoning,
    )
    return f"\n{header_line}\n{highlighted_json}\n"


def raw_request(payload: Any, highlight_keys: bool = True, highlight_reasoning: bool = True) -> str:
    """Format a raw request payload.
    
    Args:
        payload: The request payload to format.
        highlight_keys: Whether to highlight JSON object keys. Defaults to True.
    """
    return raw_json(payload, label="RAW REQUEST PAYLOAD", highlight_keys=highlight_keys)


def raw_response(response: Any, highlight_keys: bool = True, highlight_reasoning: bool = True) -> str:
    """Format a raw API response.
    
    Args:
        response: The response to format.
        highlight_keys: Whether to highlight JSON object keys. Defaults to True.
        highlight_reasoning: Whether to highlight reasoning delimiters in JSON string values. Defaults to True.
    """
    return raw_json(
        response,
        label="RAW RESPONSE",
        highlight_keys=highlight_keys,
        highlight_reasoning=highlight_reasoning,
    )


def error(text: str) -> str:
    """Format an error message."""
    return _wrap(f"ERROR: {text}", Color.BRIGHT_RED)


def warning(text: str) -> str:
    """Format a warning message."""
    return _wrap(f"WARNING: {text}", Color.BRIGHT_YELLOW)


def success(text: str) -> str:
    """Format a success message."""
    return _wrap(f"OK: {text}", Color.BRIGHT_GREEN)


def dim(text: str) -> str:
    """Format dimmed text for secondary info."""
    return _wrap(text, Color.DIM)


# ─── Reasoning/Thinking Process Highlighting ───────────────────────────

# Regex patterns for reasoning content highlighting.
# Each entry is a (compiled_regex_pattern, [color_list]) tuple.
# Color legend:
#   BOLD + BRIGHT_WHITE + BG_BLUE  →  "Thinking Process:" header (blue background, white bold text)
#   BRIGHT_CYAN + BOLD             →  Numbered section headers like "1. **Deconstruct the request:**"
#   BRIGHT_BLACK + BG_YELLOW + BOLD →  Attempt markers like "*Attempt 1:*" (yellow background, bold)
#   BRIGHT_MAGENTA + BOLD          →  Option markers like "*Option A:*" (magenta, bold)
#   BRIGHT_RED + DIM               →  Self-correction markers like "-> Fail." (red, dimmed)
_REASONING_PATTERNS = [
    (re.compile(r'(Thinking Process:)', re.MULTILINE), [Color.BOLD, Color.BRIGHT_WHITE, Color.BG_BLUE]),
    (re.compile(r'(\d+\.\s*\*\*.*:\*\*)', re.MULTILINE), [Color.BRIGHT_CYAN, Color.BOLD]),
    (re.compile(r'(\*?\s*\*?Attempt\s+\d+[^:\n]*:\*?)'), [Color.BRIGHT_BLACK, Color.BG_YELLOW, Color.BOLD]),
    (re.compile(r'(\*?\s*\*?Option\s+[A-Z]\s*[:\*]\*?)'), [Color.BRIGHT_MAGENTA, Color.BOLD]),
    (re.compile(r'(->\s+\S+[\s\.:]*)'), [Color.BRIGHT_RED]),
    (re.compile(r'(Result:)', re.MULTILINE), [Color.BRIGHT_WHITE, Color.BG_BLUE]),
]


def _highlight_reasoning(text: str) -> str:
    """
    Apply inline ANSI color codes to reasoning/thinking process text via multi-pass
    pattern matching. Each pattern is paired with its color list; passes run sequentially,
    each updating the result string.
    
    Coloring scheme:
    - "Thinking Process:" header: BOLD + BRIGHT_WHITE + BG_BLUE
    - Section headers (N. **Title**): BRIGHT_CYAN + BOLD
    - Attempt markers (*Attempt N*): BRIGHT_BLACK + BG_YELLOW + BOLD
    - Option markers (*Option X*): BRIGHT_MAGENTA + BOLD
    - Self-corrections (-> Fail.): BRIGHT_RED + DIM
    
    Args:
        text: The reasoning/thinking process text to highlight.
        
    Returns:
        The text with ANSI color codes injected at delimiter points.
    """
    result = text
    for pattern, colors in _REASONING_PATTERNS:
        result = pattern.sub(lambda m: _wrap(m.group(1), *colors), result)
    return result


def reasoning_content(content: str, label: str = "THINKING PROCESS") -> str:
    """
    Format AI reasoning/thinking process with inline-highlighted delimiters.
    
    This function wraps the content label in a color and applies inline ANSI
    highlighting to delimiter patterns within the content, preserving all
    original formatting.
    
    Args:
        content: The reasoning/thinking process text.
        label: The label to display above the content.
        
    Returns:
        The formatted string with colorized delimiters.
    """
    label_part = _wrap(f"{label}:", Color.BRIGHT_GREEN, Color.BOLD)
    content_part = _highlight_reasoning(content)
    return f"{label_part}\n{content_part}"


# ─── Convenience printer ───────────────────────────────────────────────

class Formatter:
    """
    A convenience class that wraps print() with formatting helpers.
    Usage:
        f = Formatter()
        f.header("My Section")
        f.model_input("USER", "Hello!")
        f.model_output("ASSISTANT", "Hi there!")
    """

    def __init__(self, show_raw: bool = False):
        """
        Args:
            show_raw: If True, also print raw JSON for requests and responses.
        """
        self.show_raw = show_raw
        self._raw_responses: list = []
        self._raw_requests: list = []

    def print(self, text: str = "", end: str = "\n") -> None:
        """Print plain text."""
        print(text, end=end)

    def header(self, title: str, width: int = 60) -> None:
        print(header(title, width))

    def subheader(self, title: str, width: int = 60) -> None:
        print(subheader(title, width))

    def script(self, text: str) -> None:
        print(script(text))

    def config(self, text: str) -> None:
        print(config(text))

    def model_input(self, label: str, content: str) -> None:
        print(model_input(label, content))

    def model_output(self, content: str, label: str = "ASSISTANT") -> None:
        print(model_output(content, label))

    def parsed_response(self, content: str, label: str = "ASSISTANT", width: int = 60) -> None:
        """Print a parsed response with the centralized 'PARSED RESPONSE' separator."""
        print(parsed_response(content, label, width))

    def metadata(self, label: str, value: str) -> None:
        print(metadata(label, value))

    def error(self, text: str) -> None:
        print(error(text))

    def warning(self, text: str) -> None:
        print(warning(text))

    def success(self, text: str) -> None:
        print(success(text))

    def dim(self, text: str) -> None:
        print(dim(text))

    def reasoning_content(self, content: str, label: str = "THINKING PROCESS") -> None:
        """Print reasoning/thinking process with inline-highlighted delimiters."""
        print(reasoning_content(content, label))

    def raw_request(self, payload: Any, highlight_keys: bool = True, highlight_reasoning: bool = True) -> None:
        """Print raw request. Always stored; printed if show_raw is True.
        
        Args:
            payload: The request payload to format.
            highlight_keys: Whether to highlight JSON object keys. Defaults to True.
            highlight_reasoning: Whether to highlight reasoning delimiters in JSON string values. Defaults to True.
        """
        self._raw_requests.append(payload)
        if self.show_raw:
            print(raw_request(
                payload,
                highlight_keys=highlight_keys,
                highlight_reasoning=highlight_reasoning,
            ))

    def raw_response(self, response: Any, highlight_keys: bool = True, highlight_reasoning: bool = True) -> None:
        """Print raw response. Always stored; printed if show_raw is True.
        
        Args:
            response: The response to format.
            highlight_keys: Whether to highlight JSON object keys. Defaults to True.
            highlight_reasoning: Whether to highlight reasoning delimiters in JSON string values. Defaults to True.
        """
        self._raw_responses.append(response)
        if self.show_raw:
            print(raw_response(
                response,
                highlight_keys=highlight_keys,
                highlight_reasoning=highlight_reasoning,
            ))

    def print_all_raw(self, highlight_keys: bool = True, highlight_reasoning: bool = True) -> None:
        """Print all collected raw requests and responses (if show_raw was False).
        
        Args:
            highlight_keys: Whether to highlight JSON object keys. Defaults to True.
            highlight_reasoning: Whether to highlight reasoning delimiters in JSON string values. Defaults to True.
        """
        for req in self._raw_requests:
            print(raw_request(
                req,
                highlight_keys=highlight_keys,
                highlight_reasoning=highlight_reasoning,
            ))
        for resp in self._raw_responses:
            print(raw_response(
                resp,
                highlight_keys=highlight_keys,
                highlight_reasoning=highlight_reasoning,
            ))


# ─── Quick demo ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Formatter Demo ===\n")

    f = Formatter(show_raw=True)

    f.header("DEMO: FORMATTED OUTPUT")
    f.print()
    f.config("  Base URL: https://api.example.com")
    f.config("  Model: gpt-3.5-turbo")
    f.print()
    f.model_input("SYSTEM", "You are a helpful assistant.")
    f.print()
    f.model_input("USER", "What is machine learning?")
    f.print()
    f.model_output("Machine learning is a subset of artificial intelligence...", "ASSISTANT")
    f.print()
    f.metadata("Finish Reason", "stop")
    f.metadata("Total Tokens", "128")
    f.metadata("Response Time", "1.23s")
    f.print()
    f.raw_response({
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "choices": [{"message": {"content": "Hello!"}}]
    })
    f.print()

    # Demo reasoning content highlighting
    f.subheader("REASONING CONTENT HIGHLIGHTING DEMO")
    f.print()
    sample_reasoning = """Thinking Process:

1.  **Deconstruct the request:**
    *   Topic: Programming.
    *   Form: Haiku (5-7-5 syllables).

2.  **Brainstorming themes/imagery related to programming:**
    *   Bugs, errors, fixing code.
    *   Coffee, late nights.

3.  **Drafting lines (aiming for 5-7-5):**
    *   *Attempt 1:*
        *   Code writes itself now (5)
        *   But a bug breaks all the logic (7)
        *   Fix it and run again (6) -> Fail.

    *   *Attempt 2 (Classic bug focus):*
        *   Search for missing semicolon (7)
        *   Coffee fuels the long night (5)
        *   Works at last, I smile (5)

    *   *Option A:* Final polished version
    *   *Option B:* Alternative approach

4.  **Final Selection:**
    *   I'll go with a variation of Attempt 2.

5.  **Output Generation:**
    Search for hidden bug,
    Fix the code at midnight's end,
    Works at last, I smile."""
    f.reasoning_content(sample_reasoning)
    f.print()
    f.subheader("END OF DEMO")
