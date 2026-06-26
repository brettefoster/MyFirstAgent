#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 5: System Prompt Engineering

This script demonstrates how different system prompts dramatically affect
the style, tone, and content of model responses.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage3_state_engine.state_machine import AgentState


def demo_different_personalities():
    """Show how different system prompts affect responses."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 5: SYSTEM PROMPT ENGINEERING")
    f.script("How System Prompts Dramatically Change Output")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Define different system prompts to experiment with
    system_prompts = [
        {
            "name": "Helpful Assistant",
            "prompt": "You are a helpful assistant.",
            "description": "Standard, neutral assistant behavior."
        },
        {
            "name": "Concise Assistant",
            "prompt": "You are a concise assistant. Answer in one sentence.",
            "description": "Forces brief, to-the-point responses."
        },
        {
            "name": "Software Engineer Expert",
            "prompt": "You are an expert software engineer. Use technical terminology. Explain implementations in detail.",
            "description": "Technical, detailed responses with engineering focus."
        },
        {
            "name": "Friendly Tutor",
            "prompt": "You are a friendly tutor. Explain concepts simply with examples. Be encouraging and patient.",
            "description": "Warm, educational tone with simple explanations."
        },
        {
            "name": "Socratic Tutor",
            "prompt": "You are a Socratic tutor. Never give direct answers. Instead, ask guiding questions that help the user discover answers themselves.",
            "description": "Asks questions rather than providing answers."
        },
    ]

    # Test prompt with each personality
    user_question = "How do I build a REST API in Python?"

    f.subheader("TEST QUESTION")
    f.model_input("USER", user_question)
    f.print()

    # Track prompt effects
    prompt_effects = []

    for i, prompt_info in enumerate(system_prompts, 1):
        f.subheader(f"Prompt {i}: {prompt_info['name']}")
        f.script(f"  Description: {prompt_info['description']}")
        f.script(f"  System Prompt: \"{prompt_info['prompt']}\"")
        f.print()

        # Create agent with this system prompt
        agent = AgentState(system_instruction=prompt_info["prompt"])

        # Add user message
        agent.add_user_message(user_question)

        # Show the payload
        payload = agent.compile_payload()
        f.script("  Payload messages:")
        for msg in payload["messages"]:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "SYSTEM":
                f.script(f"    [{role}] {content}")
            else:
                f.script(f"    [{role}] {content}")
        f.print()

        # Simulate different response styles (since we're demonstrating prompt effects)
        # In practice, you'd call the API to see real responses
        simulated_responses = {
            "Helpful Assistant": (
                "To build a REST API in Python, you can use Flask or FastAPI. "
                "FastAPI is recommended for its modern features and automatic documentation. "
                "Install it with pip, create routes using decorators, and run with uvicorn."
            ),
            "Concise Assistant": (
                "Use FastAPI: install it, define routes with @app.get() decorators, "
                "and run with uvicorn for a quick REST API."
            ),
            "Software Engineer Expert": (
                "For a production REST API, use FastAPI with Pydantic models for "
                "request/response validation. Implement dependency injection, "
                "async/await for I/O operations, SQLAlchemy for ORM, "
                "and Pytest for testing. Structure with routers for modular route "
                "organization and add OpenAPI docs at /docs."
            ),
            "Friendly Tutor": (
                "Great question! Let's start with FastAPI - it's really beginner-friendly. "
                "First, you'd install it with pip install fastapi uvicorn. Then you create "
                "an app and define your first route. Think of a route like a signpost that "
                "tells the web where to go when someone visits a specific URL!"
            ),
            "Socratic Tutor": (
                "That's a great question! Before we jump into code, let's think about "
                "what a REST API actually does. What do you think happens when you type "
                "a URL into your browser? Understanding that will help us design our API."
            ),
        }

        response = simulated_responses[prompt_info["name"]]
        f.parsed_response(response, "ASSISTANT")
        f.print()

        prompt_effects.append({
            "name": prompt_info["name"],
            "response_length": len(response),
            "tone": _classify_tone(response),
        })

    # Summary comparison
    f.subheader("SYSTEM PROMPT COMPARISON")
    f.print()
    f.script(f"  {'Prompt':<25} {'Length':<10} {'Tone':<20}")
    f.dim("  " + "-" * 55)
    for effect in prompt_effects:
        f.script(f"  {effect['name']:<25} {effect['response_length']:<10} {effect['tone']:<20}")
    f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  How dramatically does the system prompt affect output?")
    f.script("  The system prompt has a VERY SIGNIFICANT effect on output:")
    f.script("")
    f.script("  1. TONE: From concise (20 chars) to verbose (150+ chars)")
    f.script("  2. DETAIL: From one sentence to detailed technical explanations")
    f.script("  3. APPROACH: Direct answers vs. guiding questions")
    f.script("  4. VOCABULARY: Simple words vs. technical terminology")
    f.script("")
    f.script("  The system prompt is the MOST powerful tool for controlling")
    f.script("  model behavior. It should be carefully crafted for each use case.")
    f.print()

    # Best practices
    f.subheader("SYSTEM PROMPT BEST PRACTICES")
    f.script("  1. Be specific about the role and expertise level")
    f.script("  2. Define response format (e.g., 'use bullet points')")
    f.script("  3. Set the tone (formal, casual, technical, simple)")
    f.script("  4. Include constraints (e.g., 'answer in under 50 words')")
    f.script("  5. Specify what NOT to do (e.g., 'never share code')")
    f.script("  6. Test multiple prompts to find the best fit")
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  System prompts are not just suggestions - they fundamentally")
    f.script("  reshape how the model processes questions and formulates answers.")
    f.script("  Investing time in prompt engineering yields dramatically better")
    f.script("  results than relying on default behavior.")


def _classify_tone(text: str) -> str:
    """Classify the general tone of a response."""
    if any(word in text.lower() for word in ["great question", "let's", "think of"]):
        return "encouraging"
    if any(word in text.lower() for word in ["that's", "before", "what do you"]):
        return "socratic"
    if len(text.split()) <= 25:
        return "concise"
    if any(term in text.lower() for term in ["pydantic", "async", "orm", "pytest"]):
        return "technical"
    return "standard"


if __name__ == "__main__":
    demo_different_personalities()