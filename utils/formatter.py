#!/usr/bin/env python3
"""
Output formatter with ANSI colors for distinguishing between
script output, model input, model output, and raw JSON responses.
"""

import json
import os
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


def _wrap(text: str, color: Color) -> str:
    """Wrap text with a color code, respecting the colors enabled setting."""
    if _COLORS_ENABLED:
        return f"{color.value}{text}{Color.RESET.value}"
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


def metadata(label: str, value: str) -> str:
    """Format metadata key-value pairs (cyan)."""
    return _wrap(f"  {label}: {value}", Color.CYAN)


def raw_json(data: Any, label: str = "RAW RESPONSE") -> str:
    """
    Format raw JSON data with a colored label.
    The JSON itself is not colored (to preserve readability), but the
    surrounding label and separators are.
    """
    sep = _wrap("-" * 60, Color.DIM)
    header_line = _wrap(f"{sep}\n{label}\n{sep}", Color.BRIGHT_YELLOW)
    json_str = json.dumps(data, indent=2)
    return f"\n{header_line}\n{json_str}\n"


def raw_request(payload: Any) -> str:
    """Format a raw request payload."""
    return raw_json(payload, label="RAW REQUEST PAYLOAD")


def raw_response(response: Any) -> str:
    """Format a raw API response."""
    return raw_json(response, label="RAW RESPONSE")


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

    def raw_request(self, payload: Any) -> None:
        """Print raw request. Always stored; printed if show_raw is True."""
        self._raw_requests.append(payload)
        if self.show_raw:
            print(raw_request(payload))

    def raw_response(self, response: Any) -> None:
        """Print raw response. Always stored; printed if show_raw is True."""
        self._raw_responses.append(response)
        if self.show_raw:
            print(raw_response(response))

    def print_all_raw(self) -> None:
        """Print all collected raw requests and responses (if show_raw was False)."""
        for req in self._raw_requests:
            print(raw_request(req))
        for resp in self._raw_responses:
            print(raw_response(resp))


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
    f.subheader("END OF DEMO")