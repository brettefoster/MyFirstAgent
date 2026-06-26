#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 2: Add Custom Thinking Patterns

This script demonstrates how to extend the ThinkingObserver with custom
thinking patterns and verify they are detected correctly.
"""

import json
import re
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage2_thinking_observer.thinking_observer import (
    ThinkingObserver,
    OutputMode,
    StreamSegment,
)


class ExtendedThinkingObserver(ThinkingObserver):
    """
    Extended ThinkingObserver with custom thinking patterns.
    
    This demonstrates Exercise 2: adding custom patterns to detect
    different thinking styles and languages.
    """

    def __init__(self):
        """Initialize with extended patterns."""
        # Start with base patterns
        super().__init__()
        
        # Add custom thinking patterns
        self.THINKING_START_PATTERNS.extend([
            r"#思考",           # Chinese "think"
            r"Let me analyze",  # Analytical phrasing
            r"My reasoning is", # Explicit reasoning marker
            r"Breaking this down",  # Decomposition marker
            r"First, I'll",     # Step-by-step starter
            r"Here's my approach",  # Approach declaration
            r"*\*thinking\*",   # Markdown-style thinking marker
            r"Deep thought:",   # Explicit deep thought marker
        ])
        
        # Recompile the regex
        self.thinking_start_re = re.compile(
            "|".join(self.THINKING_START_PATTERNS),
            re.IGNORECASE
        )


def test_custom_patterns():
    """Test each custom pattern with simulated chunks."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 2: ADD CUSTOM THINKING PATTERNS")
    f.script("Extending ThinkingObserver with Custom Detection Patterns")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    observer = ExtendedThinkingObserver()

    # Test cases: each with a pattern and matching simulated input
    test_cases = [
        {
            "name": "Chinese Thinking Marker (#思考)",
            "chunks": [
                "#思考\n这个问题需要仔细分析。\n",
                "答案是42。",
            ],
            "expected_thinking": "这个问题需要仔细分析。",
        },
        {
            "name": "Analytical Phrasing (Let me analyze)",
            "chunks": [
                "Let me analyze this problem step by step.\n\n",
                "The solution is straightforward.",
            ],
            "expected_thinking": "Let me analyze this problem step by step.",
        },
        {
            "name": "Explicit Reasoning (My reasoning is)",
            "chunks": [
                "My reasoning is as follows:\n",
                "First consider the premises, then draw conclusions.",
            ],
            "expected_thinking": "My reasoning is as follows:",
        },
        {
            "name": "Decomposition (Breaking this down)",
            "chunks": [
                "Breaking this down into parts:\n",
                "Part 1: Understand the problem. Part 2: Solve it.",
            ],
            "expected_thinking": "Breaking this down into parts:",
        },
        {
            "name": "Step Starter (First, I'll)",
            "chunks": [
                "First, I'll identify the key variables.\n\n",
                "Then I'll solve for the unknown.",
            ],
            "expected_thinking": "First, I'll identify the key variables.",
        },
        {
            "name": "Approach Declaration (Here's my approach)",
            "chunks": [
                "Here's my approach to solving this:\n",
                "I will use a systematic method.",
            ],
            "expected_thinking": "Here's my approach to solving this:",
        },
        {
            "name": "Markdown Style (*\\*thinking\\*)",
            "chunks": [
                "*\\*thinking\\*\nWorking through the logic...\n",
                "The answer is clear now.",
            ],
            "expected_thinking": "*\\*thinking\\*\nWorking through the logic...",
        },
        {
            "name": "Deep Thought Marker (Deep thought:)",
            "chunks": [
                "Deep thought:\nI need to consider all possibilities.\n",
                "After evaluation, the best choice is B.",
            ],
            "expected_thinking": "Deep thought:\nI need to consider all possibilities.",
        },
    ]

    f.subheader("TESTING CUSTOM PATTERNS")
    f.print()

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        f.script(f"Test {i}: {test['name']}")
        
        observer.reset()
        
        # Feed all chunks
        for chunk in test["chunks"]:
            observer.feed_chunk(chunk)
        
        # Get extracted content
        thinking = observer.get_thinking_content()
        answer = observer.get_answer_content()
        remaining = observer.get_remaining_text()
        
        # Check if thinking was detected
        expected = test["expected_thinking"]
        if expected.lower() in thinking.lower() or any(word.lower() in thinking.lower() for word in expected.split()[:3]):
            f.success(f"  PASS - Thinking detected: {repr(thinking[:50])}...")
            passed += 1
        else:
            f.error(f"  FAIL - Thinking NOT detected. Got: {repr(thinking)}")
            failed += 1
        
        f.script(f"  Answer: {repr(answer[:50] if answer else '(empty)')}")
        f.script(f"  Remaining: {repr(remaining[:50] if remaining else '(empty)')}")
        f.print()

    # Summary
    f.subheader("RESULTS SUMMARY")
    f.script(f"  Total tests: {len(test_cases)}")
    f.success(f"  Passed: {passed}")
    if failed > 0:
        f.error(f"  Failed: {failed}")
    f.print()

    # Show all configured patterns
    f.subheader("ALL CONFIGURED THINKING START PATTERNS")
    f.script(f"  Total patterns: {len(observer.THINKING_START_PATTERNS)}")
    f.print()
    for i, pattern in enumerate(observer.THINKING_START_PATTERNS, 1):
        marker = " +" if i > len(ThinkingObserver.THINKING_START_PATTERNS) else "  "
        f.script(f"  {marker} {pattern}")
    f.print()

    f.subheader("ALL CONFIGURED THINKING END PATTERNS")
    for pattern in observer.THINKING_END_PATTERNS:
        f.script(f"    - {pattern}")
    f.print()

    # Explanation
    f.subheader("WHY CUSTOM PATTERNS MATTER")
    f.script("  Different models and prompting styles produce different thinking patterns.")
    f.script("  By extending the pattern list, you can detect reasoning in:")
    f.script("  - Multilingual models (Chinese, Japanese, etc.)")
    f.script("  - Models trained with specific reasoning frameworks")
    f.script("  - Custom system prompts that encourage specific phrasing")
    f.script("  - Domain-specific reasoning styles")
    f.print()


if __name__ == "__main__":
    test_custom_patterns()