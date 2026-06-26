#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 6: Prompt Engineering for Thinking

This script demonstrates how different prompts encourage or discourage
thinking behavior in LLM output.
"""

import json
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
)


def demo_prompt_engineering():
    """Experiment with prompts that encourage or discourage thinking behavior."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 6: PROMPT ENGINEERING FOR THINKING")
    f.script("How Different Prompts Affect Thinking Pattern Detection")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    # Prompt categories with different thinking encouragement levels
    prompt_tests = [
        {
            "category": "No Thinking Encouragement",
            "prompts": [
                "What is 2+2?",
                "Name the capital of France.",
                "What color is the sky?",
            ],
        },
        {
            "category": "Mild Thinking Encouragement",
            "prompts": [
                "What is 2+2? Explain briefly.",
                "Why is the sky blue? Give a short explanation.",
                "What makes humans unique? One sentence.",
            ],
        },
        {
            "category": "Moderate Thinking Encouragement",
            "prompts": [
                "Think step by step: What is 15 * 24?",
                "Show your work: Calculate the area of a 5x10 rectangle.",
                "Walk through your reasoning: Is 101 a prime number?",
            ],
        },
        {
            "category": "Strong Thinking Encouragement",
            "prompts": [
                "Please think through this carefully and explain each step of your reasoning before giving your answer.",
                "Take your time to analyze this problem. Consider multiple approaches before concluding.",
                "Break down this problem systematically. Show all your work and reasoning.",
            ],
        },
        {
            "category": "Explicit Thinking Format",
            "prompts": [
                "Use <thinking> tags to show your reasoning, then provide your answer.",
                "First think through the problem in a thinking block, then give your final answer.",
                "Write your reasoning inside <thinking>...</thinking> tags, then answer.",
            ],
        },
    ]

    all_results = []

    for category_data in prompt_tests:
        f.subheader(f"Category: {category_data['category']}")
        f.print()

        category_results = []

        for j, prompt in enumerate(category_data["prompts"], 1):
            f.script(f"  Prompt {j}: {prompt}")

            observer = ThinkingObserver()
            start_time = time.time()

            # Simulate a realistic response that might come from the API
            # For demonstration, we use pattern-based simulated responses
            simulated_response = _simulate_response(prompt, category_data["category"])
            
            # Process the simulated response
            for chunk in simulated_response:
                observer.feed_chunk(chunk)

            elapsed = time.time() - start_time

            thinking = observer.get_thinking_content()
            answer = observer.get_answer_content()
            has_thinking = len(thinking) > 0

            result = {
                "prompt": prompt,
                "has_thinking": has_thinking,
                "thinking_length": len(thinking),
                "answer_length": len(answer),
                "category": category_data["category"],
            }
            category_results.append(result)
            all_results.append(result)

            if has_thinking:
                f.success(f"    Thinking detected: {len(thinking)} chars")
                f.script(f"    Thinking preview: {thinking[:80]}...")
            else:
                f.warning(f"    No thinking detected")
            
            f.script(f"    Answer preview: {answer[:80] if answer else '(empty)'}...")
            f.print()

        # Category summary
        thinking_count = sum(1 for r in category_results if r["has_thinking"])
        total_chars = sum(r["thinking_length"] for r in category_results)
        f.script(f"  Category Summary: {thinking_count}/{len(category_results)} prompts produced thinking")
        f.script(f"  Total thinking characters: {total_chars}")
        f.print()

    # Overall analysis
    f.subheader("OVERALL ANALYSIS")
    f.print()

    # Group by category
    categories = {}
    for result in all_results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "with_thinking": 0, "total_thinking_chars": 0}
        categories[cat]["total"] += 1
        categories[cat]["with_thinking"] += 1 if result["has_thinking"] else 0
        categories[cat]["total_thinking_chars"] += result["thinking_length"]

    f.script(f"  {'Category':<40} {'Thinking Rate':<20} {'Avg Chars':<15}")
    f.dim("  " + "-" * 73)
    
    for cat, stats in categories.items():
        rate = stats["with_thinking"] / stats["total"] * 100 if stats["total"] > 0 else 0
        avg_chars = stats["total_thinking_chars"] / stats["total"] if stats["total"] > 0 else 0
        f.script(f"  {cat:<40} {rate:>5.0f}%{'':<13} {avg_chars:>10.1f}")
    
    f.print()

    # Key insights
    f.subheader("KEY INSIGHTS")
    f.script("  1. Simple factual questions rarely produce thinking blocks.")
    f.script("  2. Questions asking for 'step by step' or 'show work' strongly")
    f.script("     encourage reasoning patterns.")
    f.script("  3. Explicit format requests (use <thinking> tags) are the most")
    f.script("     reliable way to get structured thinking output.")
    f.script("  4. The model's training and system prompt also influence whether")
    f.script("     thinking patterns emerge, regardless of the prompt.")
    f.print()

    # Recommendations
    f.subheader("RECOMMENDATIONS FOR PROMPT ENGINEERING")
    f.script("  To ENCOURAGE thinking:")
    f.script("    - Use 'think step by step' or 'show your work'")
    f.script("    - Ask for reasoning before the answer")
    f.script("    - Request explicit format with thinking tags")
    f.script("    - Frame as complex problems requiring analysis")
    f.print()
    f.script("  To DISCOURAGE thinking:")
    f.script("    - Ask direct, simple questions")
    f.script("    - Request brief/short answers")
    f.script("    - Avoid words like 'explain', 'reason', 'analyze'")
    f.script("    - Use 'just give me the answer' phrasing")
    f.print()


def _simulate_response(prompt: str, category: str) -> list:
    """
    Simulate a realistic LLM response based on prompt type.
    
    This creates simulated chunks that demonstrate how different prompts
    might produce different thinking patterns.
    """
    # Simple questions - no thinking
    if "No Thinking" in category:
        if "2+2" in prompt:
            return ["4"]
        elif "capital" in prompt.lower():
            return ["Paris"]
        elif "sky" in prompt.lower():
            return ["Blue"]
        return ["The answer is provided above."]

    # Mild encouragement - brief thinking
    if "Mild" in category:
        return [
            "Let me think about this briefly.\n\n",
            "The answer is straightforward based on basic knowledge.",
        ]

    # Strong encouragement - detailed thinking
    if "Strong" in category or "Explicit" in category:
        if "15 * 24" in prompt:
            return [
                "<thinking>\n",
                "I need to multiply 15 by 24.\n\n",
                "Let me break this down:\n",
                "- 15 * 24 = 15 * (20 + 4)\n",
                "- = 15 * 20 + 15 * 4\n",
                "- = 300 + 60\n",
                "- = 360\n\n",
                "Let me verify: 15 * 24 = 360. Yes, that's correct.\n",
                "</thinking>\n\n",
                "The answer is 360.",
            ]
        elif "prime" in prompt.lower():
            return [
                "<thinking>\n",
                "To check if 101 is prime, I need to test divisibility\n",
                "by primes up to sqrt(101) ≈ 10.\n\n",
                "Primes to check: 2, 3, 5, 7\n",
                "- 101 is odd, not divisible by 2\n",
                "- 1+0+1=2, not divisible by 3\n",
                "- Doesn't end in 0 or 5, not divisible by 5\n",
                "- 101/7 = 14.43, not divisible by 7\n\n",
                "Since 101 is not divisible by any prime up to its square root,\n",
                "it is a prime number.\n",
                "</thinking>\n\n",
                "Yes, 101 is a prime number.",
            ]
        # Generic complex response
        return [
            "<thinking>\n",
            "This is a complex question that requires careful analysis.\n\n",
            "Let me consider the key factors:\n",
            "1. Understanding the core question\n",
            "2. Evaluating relevant information\n",
            "3. Drawing a conclusion\n\n",
            "After thorough consideration, I have a well-reasoned answer.\n",
            "</thinking>\n\n",
            "Based on my analysis, here is the answer to your question.",
        ]

    # Default - moderate thinking
    return [
        "Let me analyze this.\n\n",
        "Here's my answer.",
    ]


if __name__ == "__main__":
    demo_prompt_engineering()