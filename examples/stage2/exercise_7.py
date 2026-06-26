#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 7: Hide Thinking from User

This script demonstrates building a wrapper that shows only the answer
to users while logging thinking for debugging purposes.
"""

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from datetime import datetime

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


@dataclass
class DebugLogEntry:
    """A single entry in the debug log."""
    timestamp: str
    event: str
    content: str
    mode: str


class UserFacingAgent:
    """
    A wrapper that shows only answers to users while logging thinking
    for debugging and analysis purposes.
    
    This demonstrates Exercise 7: separating user-facing output
    from internal reasoning traces.
    """

    def __init__(self, model: str = "default"):
        """
        Initialize the agent.
        
        Args:
            model: The model name to identify in logs.
        """
        self.observer = ThinkingObserver()
        self.model = model
        self.debug_log: List[DebugLogEntry] = []
        self.session_start = datetime.now().isoformat()
        self._conversation_count = 0

    def stream_to_user(self, chunk: str) -> str:
        """
        Process a stream chunk and return only the answer portion for user display.
        
        Thinking content is silently logged for debugging.
        
        Args:
            chunk: A chunk of streamed text from the API.
            
        Returns:
            The user-visible text (answer content only).
        """
        self._log("RECEIVED_CHUNK", chunk)
        
        segments = self.observer.feed_chunk(chunk)
        
        user_text = ""
        for seg in segments:
            if seg.mode == OutputMode.ANSWER:
                user_text += seg.text
                self._log("USER_OUTPUT", seg.text)
            elif seg.mode == OutputMode.THINKING:
                self._log("THINKING_LOG", seg.text)
            else:
                self._log("UNKNOWN_SEGMENT", seg.text)

        # Handle remaining buffer
        remaining = self.observer.get_remaining_text()
        if remaining:
            mode = self.observer.current_mode
            if mode == OutputMode.ANSWER:
                user_text += remaining
                self._log("USER_OUTPUT_REMAINING", remaining)
            else:
                self._log("REMAINING_UNKNOWN", remaining)

        return user_text

    def get_debug_log(self) -> str:
        """
        Return the full thinking process as a formatted debug log.
        
        Returns:
            Formatted string containing the complete debug log.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("DEBUG LOG")
        lines.append(f"Model: {self.model}")
        lines.append(f"Session Started: {self.session_start}")
        lines.append(f"Total Conversations: {self._conversation_count}")
        lines.append(f"Total Log Entries: {len(self.debug_log)}")
        lines.append("=" * 60)
        lines.append("")

        for entry in self.debug_log:
            lines.append(f"[{entry.timestamp}] {entry.event}:")
            lines.append(f"  Mode: {entry.mode}")
            lines.append(f"  Content: {entry.content[:200]}")
            lines.append("")

        return "\n".join(lines)

    def get_thinking_summary(self) -> dict:
        """
        Get a summary of all thinking processed in this session.
        
        Returns:
            Dictionary with thinking statistics.
        """
        thinking = self.observer.get_thinking_content()
        answer = self.observer.get_answer_content()

        return {
            "model": self.model,
            "conversation_count": self._conversation_count,
            "thinking_content": thinking,
            "thinking_length": len(thinking),
            "answer_content": answer,
            "answer_length": len(answer),
            "total_log_entries": len(self.debug_log),
        }

    def reset(self):
        """Reset the agent for a new conversation."""
        self._conversation_count += 1
        self.observer.reset()
        self._log("SESSION_RESET", f"Conversation #{self._conversation_count} ended, starting new one")

    def _log(self, event: str, content: str):
        """Add an entry to the debug log."""
        entry = DebugLogEntry(
            timestamp=datetime.now().strftime("%H:%M:%S.%f")[:-3],
            event=event,
            content=content,
            mode=self.observer.current_mode.value if hasattr(self.observer.current_mode, 'value') else str(self.observer.current_mode),
        )
        self.debug_log.append(entry)


def demo_user_facing_agent():
    """Demonstrate the user-facing agent with hidden thinking."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 7: HIDE THINKING FROM USER")
    f.script("Building a Wrapper That Shows Only Answers to Users")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    # Create the user-facing agent
    agent = UserFacingAgent(model=model)

    # Simulated conversation with thinking
    f.subheader("SIMULATED CONVERSATION")
    f.print()

    # Conversation 1
    f.script(">>> User: What is 15 * 24? Think through it.")
    f.print()

    simulated_chunks_1 = [
        "<thinking>\n",
        "I need to calculate 15 * 24.\n",
        "Let me break it down:\n",
        "15 * 24 = 15 * (20 + 4)\n",
        "= 300 + 60\n",
        "= 360\n",
        "</thinking>\n\n",
        "The answer is 360.",
    ]

    f.script("  Processing stream...")
    f.print()

    user_visible_1 = agent.stream_to_user("".join(simulated_chunks_1))
    f.script(f"  User sees: {user_visible_1}")
    f.print()

    # Conversation 2
    f.script(">>> User: Explain why the sky is blue.")
    f.print()

    simulated_chunks_2 = [
        "<thinking>\n",
        "This is about atmospheric optics.\n",
        "Rayleigh scattering causes shorter wavelengths\n",
        "(blue) to scatter more than longer ones.\n",
        "</thinking>\n\n",
        "The sky appears blue due to Rayleigh scattering.",
    ]

    f.script("  Processing stream...")
    f.print()

    user_visible_2 = agent.stream_to_user("".join(simulated_chunks_2))
    f.script(f"  User sees: {user_visible_2}")
    f.print()

    # Reset for new session
    agent.reset()

    # Conversation 3 (new session)
    f.script(">>> User (new session): Is 17 prime?")
    f.print()

    simulated_chunks_3 = [
        "<thinking>\n",
        "To check primality, test divisibility up to sqrt(17).\n",
        "sqrt(17) ≈ 4.1, so check 2, 3.\n",
        "17 is not divisible by 2 or 3.\n",
        "Therefore 17 is prime.\n",
        "</thinking>\n\n",
        "Yes, 17 is a prime number.",
    ]

    f.script("  Processing stream...")
    f.print()

    user_visible_3 = agent.stream_to_user("".join(simulated_chunks_3))
    f.script(f"  User sees: {user_visible_3}")
    f.print()

    f.print()

    # Show what the user sees vs what's logged
    f.subheader("USER-VISIBLE OUTPUT (what the user sees)")
    f.script("  Conversation 1: " + user_visible_1)
    f.script("  Conversation 2: " + user_visible_2)
    f.script("  Conversation 3: " + user_visible_3)
    f.print()

    # Show debug log
    f.subheader("DEBUG LOG (internal use only - NOT shown to user)")
    debug_log = agent.get_debug_log()
    for line in debug_log.split("\n")[:40]:  # Show first 40 lines
        f.script(f"  {line}")
    if debug_log.count("\n") > 40:
        remaining = debug_log.count("\n") - 40
        f.script(f"  ... ({remaining} more log entries)")
    f.print()

    # Show summary
    f.subheader("SESSION SUMMARY")
    summary = agent.get_thinking_summary()
    f.metadata("Model", summary["model"])
    f.metadata("Conversations", str(summary["conversation_count"]))
    f.metadata("Total Thinking Chars", str(summary["thinking_length"]))
    f.metadata("Total Answer Chars", str(summary["answer_length"]))
    f.metadata("Debug Log Entries", str(summary["total_log_entries"]))
    f.print()

    # Use cases
    f.subheader("USE CASES")
    f.script("  This pattern is useful for:")
    f.script("  1. Production APIs: Show clean answers, log reasoning internally")
    f.script("  2. Debugging: Developers can inspect thinking without affecting users")
    f.script("  3. Training: Collect thinking data for model improvement")
    f.script("  4. Auditing: Track reasoning for compliance requirements")
    f.script("  5. Analytics: Analyze thinking patterns across conversations")
    f.print()

    # Architecture diagram
    f.subheader("ARCHITECTURE")
    f.script("  ┌─────────────┐     ┌──────────────────┐     ┌──────────┐")
    f.script("  │  API Stream │────▶│  ThinkingObserver │────▶│  Agent   │")
    f.script("  └─────────────┘     └──────────────────┘     └────┬─────┘")
    f.script("                                                     │")
    f.script("                          ┌──────────────────────────┤")
    f.script("                          │          ┌───────────────┤")
    f.script("                          ▼          ▼               ▼")
    f.script("                   ┌──────────┐  ┌──────┐    ┌──────────┐")
    f.script("                   │  User    │  │Debug │    │ Thinking │")
    f.script("                   │  Facing  │  │  Log │    │  Summary │")
    f.script("                   └──────────┘  └──────┘    └──────────┘")
    f.print()


if __name__ == "__main__":
    demo_user_facing_agent()