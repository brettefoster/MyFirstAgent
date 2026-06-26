#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 7: Context Summarization

This script demonstrates building a summarization strategy for old messages
when the conversation exceeds a threshold, preserving key information while
reducing context size.
"""

import json
import sys
from typing import List, Dict, Any
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage3_state_engine.state_machine import AgentState


class SummarizedState(AgentState):
    """
    Extended AgentState with summarization for old messages.

    When the conversation exceeds a threshold, older messages are replaced
    with a summary to preserve key information while reducing context size.
    """

    def __init__(self, system_instruction: str = "You are a helpful assistant.", summary_threshold: int = 20):
        """
        Initialize the summarized state.

        Args:
            system_instruction: The system prompt that guides the model's behavior.
            summary_threshold: Number of messages after which summarization is triggered.
        """
        super().__init__(system_instruction)
        self.summary_threshold = summary_threshold
        self.summary = ""

    def maybe_summarize(self) -> bool:
        """
        Check if summarization should be triggered and perform it.

        Returns:
            True if summarization was performed, False otherwise.
        """
        if len(self.history) > self.summary_threshold:
            self._summarize_old_messages()
            return True
        return False

    def _summarize_old_messages(self) -> None:
        """
        Summarize older messages and keep only recent ones.

        In a real implementation, this would call an LLM to generate
        a summary. Here we simulate the summary with a condensed version
        of the key information.
        """
        # Split into old and recent messages
        old_messages = self.history[:self.summary_threshold]
        recent_messages = self.history[self.summary_threshold:]

        # Generate a simulated summary
        self.summary = self._generate_summary(old_messages)

        # Keep only recent messages in history
        self.history = recent_messages

    def _generate_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the given messages.

        In a real implementation, this would call an LLM.
        Here we extract key facts and information.

        Args:
            messages: List of message dictionaries to summarize.

        Returns:
            A summary string.
        """
        # Extract key information from messages
        user_info = []
        topics = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user":
                # Look for personal information patterns
                if "my name is" in content.lower() or "i'm" in content.lower():
                    user_info.append(f"User introduced themselves: {content}")
                elif "i'm" in content.lower() or "i work" in content.lower():
                    user_info.append(f"User shared about themselves: {content}")
                elif "i like" in content.lower() or "i'm interested" in content.lower():
                    topics.append(f"User interest: {content}")
            elif role == "assistant":
                # Extract key topics discussed
                topic_keywords = ["machine learning", "python", "AI", "deep learning",
                                  "neural network", "NLP", "API", "data"]
                for keyword in topic_keywords:
                    if keyword.lower() in content.lower():
                        topics.append(f"Discussed: {keyword}")
                        break

        # Build summary
        summary_parts = ["Conversation Summary:", ""]
        if user_info:
            summary_parts.append("  User Information:")
            for info in user_info:
                summary_parts.append(f"    - {info}")
        if topics:
            summary_parts.append("  Topics Discussed:")
            for topic in topics:
                summary_parts.append(f"    - {topic}")

        return "\n".join(summary_parts)

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message and check if summarization is needed.

        Args:
            role: The message role ('user' or 'assistant').
            content: The message content.

        Returns:
            True if summarization was triggered.
        """
        if role == "user":
            self.add_user_message(content)
        else:
            self.add_model_message(content)

        return self.maybe_summarize()

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get messages, prepending the summary if one exists.

        Returns:
            List of messages with summary prepended if available.
        """
        messages = super().get_messages()
        if self.summary:
            # Add summary as a special system-like message
            summary_message = {
                "role": "system",
                "content": f"[CONVERSATION SUMMARY]\n{self.summary}"
            }
            return [summary_message] + messages
        return messages

    def compile_payload(self) -> Dict[str, Any]:
        """
        Compile the current state into the payload format, including summary.

        Returns:
            A dictionary in the format expected by the OpenAI-compatible API.
        """
        messages = [{"role": "system", "content": self.system_instruction}]
        messages.extend(self.get_messages())
        return {"messages": messages}

    def __repr__(self) -> str:
        """Return a string representation including summary info."""
        base = super().__repr__()
        summary_info = f", summary_threshold={self.summary_threshold}"
        if self.summary:
            summary_info += f", summary_length={len(self.summary)} chars"
        return base + summary_info


def demo_context_summarization():
    """Demonstrate context summarization with a long conversation."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 7: CONTEXT SUMMARIZATION")
    f.script("Preserving Key Information While Managing Context Size")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Create summarized state with a low threshold for demonstration
    threshold = 8  # Summarize after 8 messages
    agent = SummarizedState(
        system_instruction="You are a helpful assistant. You have access to conversation summaries for context.",
        summary_threshold=threshold
    )

    f.subheader("CONFIGURATION")
    f.script(f"  Summary threshold: {threshold} messages")
    f.script(f"  This means summarization triggers after {threshold} messages")
    f.print()

    # Simulate a long conversation
    long_conversation = [
        ("user", "Hi, I'm Alice. I'm a software developer."),
        ("assistant", "Hello Alice! Great to meet you. What kind of software do you develop?"),
        ("user", "I mainly work with Python, focusing on data science and ML."),
        ("assistant", "That sounds fascinating! Data science is a rapidly growing field."),
        ("user", "Yes! I'm currently working on a project analyzing social media trends."),
        ("assistant", "Interesting! Are you using NLP techniques for the text analysis?"),
        ("user", "Yes, we use transformers for sentiment analysis and topic modeling."),
        ("assistant", "Transformers are perfect for that. Are you using pre-trained models?"),
        ("user", "We started with BERT but are experimenting with newer models like RoBERTa."),
        ("assistant", "RoBERTa is excellent. Has it improved your results?"),
        ("user", "Significantly! Our F1 score went up by 5 percentage points."),
        ("assistant", "That's a substantial improvement. Are you fine-tuning on your data?"),
        ("user", "Yes, we fine-tune on a labeled dataset of 50K social media posts."),
        ("assistant", "Great dataset size. Are you handling class imbalance?"),
        ("user", "We use weighted loss functions and oversampling for minority classes."),
        ("assistant", "Smart approach. What about handling noisy labels in social media data?"),
        ("user", "We use label cleaning techniques and remove spam/irrelevant posts first."),
        ("assistant", "Good data preprocessing is key. Are you deploying this model?"),
        ("user", "Yes, it's in production serving real-time sentiment predictions."),
        ("assistant", "Impressive! What's your inference latency?"),
        ("user", "About 50ms per post on GPU, which meets our real-time requirements."),
    ]

    f.subheader("CONVERSATION WITH AUTOMATIC SUMMARIZATION")
    f.print()

    # Track summarization events
    summary_events = []

    for i, (role, text) in enumerate(long_conversation, 1):
        summarized = agent.add_message(role, text)

        f.script(f"  Turn {i:2d}: history={len(agent):2d} msgs", )
        if agent.summary:
            f.script(f"  |  Summary active: {len(agent.summary)} chars")
        f.script(f"  |  Context size: {agent.get_context_size()} chars")

        if summarized:
            f.script(f"  |  ** SUMMARIZATION TRIGGERED **")
            summary_events.append(i)

        f.print()

    # Show the summary that was generated
    if agent.summary:
        f.subheader("GENERATED SUMMARY")
        f.script(agent.summary)
        f.print()

    # Compare context sizes
    f.subheader("CONTEXT SIZE COMPARISON")
    f.print()

    # Calculate what context would be without summarization
    full_agent = AgentState(agent.system_instruction)
    for role, text in long_conversation:
        if role == "user":
            full_agent.add_user_message(text)
        else:
            full_agent.add_model_message(text)

    full_context_size = full_agent.get_context_size()
    summarized_context_size = agent.get_context_size()
    savings = full_context_size - summarized_context_size

    f.script(f"  Full context (no summarization): {full_context_size:,} chars")
    f.script(f"  Summarized context:              {summarized_context_size:,} chars")
    f.script(f"  Context savings:                 {savings:,} chars ({savings/full_context_size*100:.1f}%)")
    f.print()

    # Show the payload
    f.subheader("PAYLOAD WITH SUMMARY")
    payload = agent.compile_payload()
    f.raw_request(payload)
    f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  What information is lost when summarizing?")
    f.print()
    f.script("  1. EXACT WORDING: The precise phrasing of messages is lost.")
    f.script("     Summary captures the gist, not the exact text.")
    f.print()
    f.script("  2. NUANCE: Subtle nuances in conversation may be diluted.")
    f.script("     A summary is inherently less detailed.")
    f.print()
    f.script("  3. QUOTES/DATA: Specific code snippets, exact numbers,")
    f.script("     and quoted text may be paraphrased or omitted.")
    f.print()
    f.script("  4. TONE: The emotional tone of individual messages may")
    f.script("     not be fully preserved in a factual summary.")
    f.print()
    f.script("  However, a good summary preserves:")
    f.script("    - Key facts and information")
    f.script("    - User preferences and identity details")
    f.script("    - Topics and decisions discussed")
    f.script("    - Outcomes and conclusions")
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Context summarization is essential for very long conversations.")
    f.script("  It trades some detail for the ability to maintain context over")
    f.script("  many turns. The quality of the summary directly impacts how well")
    f.script("  the model can continue the conversation meaningfully.")
    f.print()
    f.subheader("PRACTICAL CONSIDERATIONS")
    f.script("  - In production, use an LLM to generate high-quality summaries")
    f.script("  - Consider summarizing in chunks (e.g., summarize every N messages)")
    f.script("  - Keep the most recent messages uncompressed for immediate context")
    f.script("  - Test different thresholds to find the right balance")


if __name__ == "__main__":
    demo_context_summarization()