#!/usr/bin/env python3
"""
Stage 2: The Thinking Pattern Observer

This module demonstrates how to detect and visualize thinking patterns
in streaming LLM output. It shows how models reason before answering.

Run with: python thinking_observer.py
"""

import json
import re
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload

@dataclass
class ThinkingMetrics:
    """Metrics for tracking thinking vs answer behavior."""
    thinking_duration: float = 0.0  # Time spent in thinking mode
    answer_duration: float = 0.0    # Time spent in answer mode
    thinking_token_count: int = 0
    answer_token_count: int = 0


class OutputMode(Enum):
    """Types of output in the stream."""
    THINKING = "thinking"
    ANSWER = "answer"
    UNKNOWN = "unknown"


@dataclass
class StreamSegment:
    """A segment of streamed output with its mode."""
    text: str
    mode: OutputMode
    timestamp: float


class UserFacingAgent:
    """Wrapper that shows only answers to users but logs thinking for debugging."""
    
    def __init__(self):
        """Initialize the user-facing agent."""
        self.observer = ThinkingObserver()
    
    def stream_to_user(self, chunk):
        """Only show answer to user."""
        segments = self.observer.feed_chunk(chunk)
        for seg in segments:
            if seg.mode == OutputMode.ANSWER:
                print(seg.text, end="", flush=True)
            # Thinking is silently logged
    
    def get_debug_log(self):
        """Return full thinking process for debugging."""
        return self.observer.get_thinking_content()


class ThinkingObserver:
    """
    Observes and categorizes streaming output into thinking vs answer.
    
    This observer detects various thinking patterns:
    1. XML-style tags: <thinking>...</thinking>
    2. Chain-of-thought markers
    3. Self-correction patterns
    """
    
    # Patterns that indicate thinking mode
    THINKING_START_PATTERNS = [
        r"<thinking>",
        r"thought:",
        r"let me think",
        r"to solve this",
        r"step by step",
        r"first, i need to",
        r"let me break this down",
        r"analysis:",
        r"reasoning:",
        r"#思考",  # Chinese "think"
        r"Let me analyze",
        r"My reasoning is",
    ]
    
    THINKING_END_PATTERNS = [
        r"</thinking>",
        r"\n\n",  # Double newline often separates thinking from answer
        r"based on my analysis",
        r"in conclusion",
        r"the answer is",
    ]
    
    # Patterns that indicate answer mode
    ANSWER_START_PATTERNS = [
        r"</thinking>\s*\n",
        r"the answer",
        r"in summary",
        r"conclusion",
    ]
    
    def __init__(self):
        """Initialize the thinking observer."""
        self.buffer = ""
        self.current_mode = OutputMode.UNKNOWN
        self.segments: List[StreamSegment] = []
        self.in_thinking_block = False
        self.metrics = ThinkingMetrics()
        self.last_mode_change = time.time()
        
        # Compile patterns for efficiency
        self.thinking_start_re = re.compile(
            "|".join(self.THINKING_START_PATTERNS), 
            re.IGNORECASE
        )
        self.thinking_end_re = re.compile(
            "|".join(self.THINKING_END_PATTERNS), 
            re.IGNORECASE
        )
        self.answer_start_re = re.compile(
            "|".join(self.ANSWER_START_PATTERNS), 
            re.IGNORECASE
        )
    
    def feed_chunk(self, chunk: str) -> List[StreamSegment]:
        """
        Feed a chunk of text and get categorized segments.
        
        Args:
            chunk: A chunk of streamed text.
            
        Returns:
            List of StreamSegment objects with categorized output.
        """
        self.buffer += chunk
        segments = []
        
        # Check for thinking block boundaries
        if not self.in_thinking_block:
            # Look for start of thinking
            match = self.thinking_start_re.search(self.buffer)
            if match:
                # Text before thinking is answer/unknown
                before_thinking = self.buffer[:match.start()]
                if before_thinking:
                    segments.append(StreamSegment(
                        text=before_thinking,
                        mode=OutputMode.ANSWER if self.current_mode == OutputMode.ANSWER else OutputMode.UNKNOWN,
                        timestamp=time.time()
                    ))
                
                self.in_thinking_block = True
                self.current_mode = OutputMode.THINKING
        
        if self.in_thinking_block:
            # Look for end of thinking block
            match = self.thinking_end_re.search(self.buffer)
            if match:
                # Extract thinking content
                thinking_content = self.buffer[:match.end()]
                segments.append(StreamSegment(
                    text=thinking_content,
                    mode=OutputMode.THINKING,
                    timestamp=time.time()
                ))
                
                # Remaining buffer is answer
                self.buffer = self.buffer[match.end():]
                self.in_thinking_block = False
                self.current_mode = OutputMode.ANSWER
        
        # Store segments
        self.segments.extend(segments)
        
        return segments
    
    def get_remaining_text(self) -> str:
        """Get any remaining text in the buffer."""
        return self.buffer
    
    def get_thinking_content(self) -> str:
        """Get all thinking content extracted so far."""
        return "".join(
            seg.text for seg in self.segments 
            if seg.mode == OutputMode.THINKING
        )
    
    def get_answer_content(self) -> str:
        """Get all answer content extracted so far."""
        return "".join(
            seg.text for seg in self.segments 
            if seg.mode == OutputMode.ANSWER
        )
    
    def reset(self):
        """Reset the observer state."""
        self.buffer = ""
        self.current_mode = OutputMode.UNKNOWN
        self.segments = []
        self.in_thinking_block = False


def format_output_with_colors(text: str, mode: OutputMode) -> str:
    """Format text with ANSI colors based on mode."""
    COLORS = {
        OutputMode.THINKING: "\033[90m",  # Gray
        OutputMode.ANSWER: "\033[92m",    # Green
        OutputMode.UNKNOWN: "\033[0m",    # Default
    }
    RESET = "\033[0m"
    
    color = COLORS.get(mode, COLORS[OutputMode.UNKNOWN])
    return f"{color}{text}{RESET}"


def demo_streaming_with_thinking():
    """Demonstrate streaming with thinking pattern detection."""
    print("\n" + "=" * 60)
    print("STAGE 2: THE THINKING PATTERN OBSERVER")
    print("Detecting Reasoning in Streaming Output")
    print("=" * 60 + "\n")
    
    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key
    
    print(f"Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print()
    
    client = APIClient(base_url=base_url, model=model, api_key=api_key)
    
    # Prompt that might trigger thinking behavior
    prompt = """Please think through this problem step by step:

If I have 3 apples and I give away 1, then buy 2 more, 
how many apples do I have? Explain your reasoning."""
    
    print(f"Prompt: {prompt}")
    print("\n" + "-" * 60)
    print("STREAMING OUTPUT (gray=thinking, green=answer):")
    print("-" * 60 + "\n")
    
    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        stream=True
    )
    
    observer = ThinkingObserver()
    full_text = ""
    start_time = time.time()
    
    for chunk in client.stream(payload):
        if not chunk or "_raw" in chunk:
            continue
        
        choice = chunk.get("choices", [{}])[0]
        delta = choice.get("delta", {})
        content = delta.get("content", "")
        
        if content:
            full_text += content
            
            # Feed through observer
            segments = observer.feed_chunk(content)
            
            for segment in segments:
                formatted = format_output_with_colors(segment.text, segment.mode)
                print(formatted, end="", flush=True)
    
    # Print any remaining text
    remaining = observer.get_remaining_text()
    if remaining:
        print(format_output_with_colors(remaining, OutputMode.UNKNOWN), end="")
    
    elapsed = time.time() - start_time
    
    print("\n" + "\n" + "-" * 60)
    print("SUMMARY:")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Thinking content length: {len(observer.get_thinking_content())} chars")
    print(f"  Answer content length: {len(observer.get_answer_content())} chars")


def demo_simulated_thinking():
    """Demonstrate with simulated thinking blocks."""
    print("\n" + "=" * 60)
    print("SIMULATED THINKING BLOCKS")
    print("=" * 60 + "\n")
    
    observer = ThinkingObserver()
    
    # Simulated stream with explicit thinking block
    simulated_chunks = [
        "<thinking>\n",
        "The user is asking about a simple math problem.\n",
        "Let me work through it:\n",
        "- Start with 3 apples\n",
        "- Give away 1: 3 - 1 = 2\n",
        "- Buy 2 more: 2 + 2 = 4\n",
        "So the answer should be 4 apples.\n</thinking>\n\n",
        "You have ",
        "4",
        " apples in total.\n",
    ]
    
    print("Simulated stream input:")
    for chunk in simulated_chunks:
        print(f"  Chunk: {repr(chunk)}")
        segments = observer.feed_chunk(chunk)
        for seg in segments:
            mode_str = "THINKING" if seg.mode == OutputMode.THINKING else "ANSWER"
            print(f"    -> [{mode_str}] {repr(seg.text)}")
    
    print("\n" + "-" * 60)
    print("EXTRACTED CONTENT:")
    print(f"\nTHINKING:\n{observer.get_thinking_content()}")
    print(f"\nANSWER:\n{observer.get_answer_content()}")


def demo_visualization():
    """Show thinking in a box, answer normally."""
    print("\n" + "=" * 60)
    print("THINKING VISUALIZATION DEMO")
    print("=" * 60 + "\n")
    
    observer = ThinkingObserver()
    
    # Simulated stream
    chunks = [
        "<thinking>\nAnalyzing the problem...\n</thinking>\n\n",
        "The answer is 42."
    ]
    
    print("Input chunks:")
    for chunk in chunks:
        print(f"  {repr(chunk)}")
    
    print("\nOutput with visualization:")
    for chunk in chunks:
        segments = observer.feed_chunk(chunk)
        for seg in segments:
            if seg.mode == OutputMode.THINKING:
                print(f"[THINKING]: {seg.text}")
            else:
                print(f"[ANSWER]: {seg.text}")


def demo_prompt_engineering():
    """Demonstrate prompt engineering for thinking behavior."""
    print("\n" + "=" * 60)
    print("PROMPT ENGINEERING FOR THINKING")
    print("=" * 60 + "\n")
    
    prompts = [
        "What is 2+2?",  # Simple, no thinking
        "Think step by step: What is 2+2?",  # Encourages thinking
        "Show your work: Calculate 15 * 24",  # Explicit reasoning request
    ]
    
    print("Testing different prompts:")
    for i, prompt in enumerate(prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        
        # Create a simple observer to demonstrate
        observer = ThinkingObserver()
        
        # Simulate responses for each prompt
        if "2+2" in prompt:
            # Simple response
            response_chunks = [
                "Let me calculate this step by step.\n\n",
                "First, I need to add 2 + 2.\n\n",
                "This equals 4.\n\n",
                "The answer is 4."
            ]
        elif "15 * 24" in prompt:
            # More complex response
            response_chunks = [
                "To calculate 15 * 24, I'll break it down.\n\n",
                "First, let me think about this multiplication.\n\n",
                "I can calculate it as: 15 * 20 + 15 * 4\n\n",
                "That's: 300 + 60 = 360.\n\n",
                "So the answer is 360."
            ]
        else:
            # Simple response
            response_chunks = [
                "The answer is 4."
            ]
        
        print("Simulated response:")
        for chunk in response_chunks:
            segments = observer.feed_chunk(chunk)
            for seg in segments:
                mode_str = "THINKING" if seg.mode == OutputMode.THINKING else "ANSWER"
                print(f"  [{mode_str}] {repr(chunk)}")


def demo_chain_of_thought():
    """Demonstrate chain-of-thought detection."""
    print("\n" + "=" * 60)
    print("CHAIN-OF-THOUGHT DETECTION")
    print("=" * 60 + "\n")
    
    observer = ThinkingObserver()
    
    # Simulated chain-of-thought without explicit tags
    cot_chunks = [
        "To solve this problem, let me break it down step by step.\n\n",
        "First, I need to understand what's being asked. ",
        "The user wants to know the final count of apples.\n\n",
        "Starting with 3 apples, giving away 1 leaves us with 2. ",
        "Then buying 2 more gives us 4 total.\n\n",
        "The answer is 4 apples."
    ]
    
    print("Chain-of-thought stream:")
    full_output = ""
    for chunk in cot_chunks:
        full_output += chunk
        segments = observer.feed_chunk(chunk)
        for seg in segments:
            mode_str = "THINKING" if seg.mode == OutputMode.THINKING else "ANSWER"
            print(f"  [{mode_str}] {repr(chunk)}")
    
    print("\n" + "-" * 60)
    print(f"Total output: {full_output}")


def main():
    """Main entry point."""
    demo_simulated_thinking()
    demo_chain_of_thought()
    demo_visualization()
    demo_prompt_engineering()
    
    # Uncomment to test with real API:
    # demo_streaming_with_thinking()


if __name__ == "__main__":
    main()