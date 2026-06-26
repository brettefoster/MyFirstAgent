#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 5: Self-Evaluation

This script demonstrates adding a self-evaluation step where the agent
critiques its own output before considering it complete.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatting utilities
from utils.config import config
from utils.formatter import Formatter


def evaluate_response(llm_response: str, user_request: str, criteria: list = None) -> dict:
    """
    Evaluate a response against a set of criteria.
    
    In a real implementation, this would call an LLM to self-evaluate.
    Here we simulate the evaluation with structured scoring.
    
    Args:
        llm_response: The response text to evaluate.
        user_request: The original user request.
        criteria: List of evaluation criteria. Defaults to common ones.
    
    Returns:
        Dictionary with evaluation scores and feedback.
    """
    if criteria is None:
        criteria = [
            "Did you answer the question directly?",
            "Is the information accurate and relevant?",
            "Did you use appropriate tools or methods?",
            "Is the response well-structured and clear?",
        ]

    # Simulate evaluation scoring (in production, this would be an LLM call)
    response_length = len(llm_response)
    has_direct_answer = llm_response.strip().startswith(("Yes,", "No,", "Here", "The", "I"))
    has_structure = "\n" in llm_response or "- " in llm_response

    scores = {
        "direct_answer": 1 if has_direct_answer else 0.5,
        "accuracy": min(1.0, response_length / 100),
        "tool_usage": 0.8 if "tool" in llm_response.lower() else 0.5,
        "clarity": min(1.0, response_length / 150),
    }

    overall_score = sum(scores.values()) / len(scores)
    is_adequate = overall_score >= 0.6

    # Generate improvement suggestions
    improvements = []
    if not has_direct_answer:
        improvements.append("Start with a direct answer to the question.")
    if response_length < 50:
        improvements.append("Provide more detail and explanation.")
    if not has_structure:
        improvements.append("Use formatting (lists, paragraphs) for readability.")

    return {
        "scores": scores,
        "overall_score": round(overall_score, 2),
        "is_adequate": is_adequate,
        "improvements": improvements,
        "evaluation_prompt": _build_evaluation_prompt(user_request, llm_response, criteria),
    }


def _build_evaluation_prompt(user_request: str, llm_response: str, criteria: list) -> str:
    """Build the prompt for LLM self-evaluation."""
    criteria_text = "\n".join(f"    {i+1}. {c}" for i, c in enumerate(criteria))
    return f"""Evaluate if your previous response adequately addressed this request:

Request: {user_request}
Response: {llm_response}

Consider:
{criteria_text}

If the response is inadequate, explain what's missing and how to improve.
"""


def demo_self_evaluation():
    """Demonstrate self-evaluation with different response qualities."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 5: SELF-EVALUATION")
    f.script("Adding Self-Evaluation to Improve Response Quality")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Sample user requests and responses of varying quality
    test_cases = [
        {
            "request": "What is the capital of France?",
            "response": "Paris",
            "label": "Short Direct Answer",
        },
        {
            "request": "Explain machine learning in simple terms.",
            "response": (
                "Machine learning is a type of artificial intelligence that allows computers "
                "to learn from data without being explicitly programmed for every specific rule.\n\n"
                "Think of it like teaching a child to recognize animals:\n"
                "- You show them many pictures of cats and dogs\n"
                "- Over time, they learn the patterns that distinguish cats from dogs\n"
                "- Now they can identify animals they've never seen before\n\n"
                "Similarly, ML algorithms find patterns in data and use those patterns "
                "to make predictions about new, unseen data."
            ),
            "label": "Detailed Explanation",
        },
        {
            "request": "Write a Python function to calculate Fibonacci numbers.",
            "response": "I don't know how to do that.",
            "label": "Poor Response",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        f.subheader(f"Test Case {i}: {case['label']}")
        f.model_input("USER REQUEST", case["request"])
        f.print()
        f.model_output("MODEL RESPONSE", case["response"])
        f.print()

        # Run self-evaluation
        evaluation = evaluate_response(case["response"], case["request"])

        f.subheader("SELF-EVALUATION RESULT")
        f.metadata("Overall Score", f"{evaluation['overall_score']:.2f} / 1.00")
        f.metadata("Adequate?", "Yes ✓" if evaluation["is_adequate"] else "No ✗")
        f.print()

        f.script("  Individual Criteria Scores:")
        for criterion, score in evaluation["scores"].items():
            label = criterion.replace("_", " ").title()
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            f.script(f"    {label:25s} [{bar}] {score:.2f}")
        f.print()

        if evaluation["improvements"]:
            f.script("  Suggested Improvements:")
            for improvement in evaluation["improvements"]:
                f.script(f"    • {improvement}")
            f.print()

        # Show the evaluation prompt that would be sent to LLM
        f.script("  Evaluation Prompt (would be sent to LLM):")
        f.model_input("EVALUATION", evaluation["evaluation_prompt"].strip())
        f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Self-evaluation helps the agent:")
    f.script("  1. Catch inadequate responses before final output")
    f.script("  2. Generate improvement suggestions automatically")
    f.script("  3. Learn from past mistakes over time")
    f.script("")
    f.script("  Question: Does self-evaluation improve response quality?")
    f.script("  Answer: Yes, when the evaluation criteria are well-designed")
    f.script("          and the LLM can honestly assess its own output.")


if __name__ == "__main__":
    demo_self_evaluation()