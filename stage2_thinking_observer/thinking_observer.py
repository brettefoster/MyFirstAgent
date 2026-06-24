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
    
    # Uncomment to test with real API:
    # demo_streaming_with_thinking()


if __name__ == "__main__":
    main()