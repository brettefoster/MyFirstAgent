#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 5: Thinking Metrics

This script demonstrates adding metrics tracking to ThinkingObserver,
including timing and token counts for thinking vs answer modes.
"""

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

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
class ThinkingMetrics:
    """Metrics for tracking thinking vs answer characteristics."""
    thinking_duration: float = 0.0       # Time spent in thinking mode (seconds)
    answer_duration: float = 0.0         # Time spent in answer mode (seconds)
    thinking_token_count: int = 0        # Estimated thinking tokens
    answer_token_count: int = 0          # Estimated answer tokens
    total_segments: int = 0              # Total segments processed
    thinking_segments: int = 0           # Number of thinking segments
    answer_segments: int = 0             # Number of answer segments
    unknown_segments: int = 0            # Number of unknown segments
    mode_switches: int = 0               # Number of times mode changed
    last_mode_switch_time: float = 0.0   # Timestamp of last mode switch
    start_time: float = 0.0              # When tracking started
    end_time: float = 0.0                # When tracking ended


class MetricsThinkingObserver(ThinkingObserver):
    """
    Extended ThinkingObserver with metrics tracking.
    
    This demonstrates Exercise 5: adding metrics to understand
    the characteristics of thinking vs answer output.
    """

    def __init__(self):
        """Initialize with metrics tracking."""
        super().__init__()
        self.metrics = ThinkingMetrics()
        self._current_mode_start = 0.0
        self._previous_mode = OutputMode.UNKNOWN

    def feed_chunk(self, chunk: str) -> List[StreamSegment]:
        """Feed a chunk and track metrics."""
        # Track start time
        if self.metrics.start_time == 0.0:
            self.metrics.start_time = time.time()
            self._current_mode_start = time.time()

        # Track mode switches
        segments = super().feed_chunk(chunk)

        for seg in segments:
            if seg.mode != self._previous_mode and self._previous_mode != OutputMode.UNKNOWN:
                # Record duration for previous mode
                duration = time.time() - self._current_mode_start
                if self._previous_mode == OutputMode.THINKING:
                    self.metrics.thinking_duration += duration
                    self.metrics.thinking_segments += 1
                elif self._previous_mode == OutputMode.ANSWER:
                    self.metrics.answer_duration += duration
                    self.metrics.answer_segments += 1
                
                self.metrics.mode_switches += 1
                self.metrics.last_mode_switch_time = time.time()

            self._previous_mode = seg.mode
            self.metrics.total_segments += 1
            self._current_mode_start = time.time()

        return segments

    def finalize_metrics(self) -> ThinkingMetrics:
        """Finalize and return metrics."""
        self.metrics.end_time = time.time()
        self.metrics.thinking_duration = round(self.metrics.thinking_duration, 4)
        self.metrics.answer_duration = round(self.metrics.answer_duration, 4)
        
        # Estimate token counts (rough approximation: ~4 chars per token)
        self.metrics.thinking_token_count = len(self.get_thinking_content()) // 4
        self.metrics.answer_token_count = len(self.get_answer_content()) // 4
        
        return self.metrics

    def reset(self):
        """Reset with metrics."""
        super().reset()
        self.metrics = ThinkingMetrics()
        self._current_mode_start = 0.0
        self._previous_mode = OutputMode.UNKNOWN


def demo_thinking_metrics():
    """Demonstrate metrics tracking with simulated streams."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 5: THINKING METRICS")
    f.script("Tracking Timing and Token Counts for Thinking vs Answer")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    # Test scenarios with different thinking/answer ratios
    scenarios = [
        {
            "name": "Quick Answer (Minimal Thinking)",
            "chunks": [
                "The answer is 42.",
            ],
        },
        {
            "name": "Moderate Reasoning",
            "chunks": [
                "<thinking>\n",
                "Let me think about this.\n",
                "The user asks a simple question.\n",
                "I should give a direct answer.\n",
                "</thinking>\n\n",
                "The answer is 42.",
            ],
        },
        {
            "name": "Deep Analysis (Extensive Thinking)",
            "chunks": [
                "<thinking>\n",
                "This is a complex question that requires careful analysis.\n\n",
                "First, I need to understand the key components:\n",
                "1. The main subject\n",
                "2. The context\n",
                "3. The expected output\n\n",
                "Let me consider each component:\n",
                "- Component 1: This relates to fundamental concepts\n",
                "- Component 2: The context suggests advanced understanding\n",
                "- Component 3: A detailed response is needed\n\n",
                "After careful consideration, I believe the best approach\n",
                "is to provide a comprehensive explanation.\n",
                "</thinking>\n\n",
                "Based on my thorough analysis, here is a comprehensive\n",
                "explanation of the topic. The key points to understand\n",
                "are the fundamental concepts, the contextual factors,\n",
                "and the expected outcomes. Each of these elements\n",
                "contributes to the overall understanding.",
            ],
        },
        {
            "name": "Multiple Switches (Thinking-Answer-Thinking-Answer)",
            "chunks": [
                "Initial thought: ",
                "<thinking>\n",
                "Wait, I need to reconsider.\n",
                "Let me think more carefully.\n",
                "</thinking>\n\n",
                "Actually, the answer is more nuanced. ",
                "<thinking>\n",
                "One more consideration: edge cases.\n",
                "</thinking>\n\n",
                "Taking edge cases into account, the final answer is...",
            ],
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        f.subheader(f"Scenario {i}: {scenario['name']}")
        f.print()

        observer = MetricsThinkingObserver()
        start_time = time.time()

        # Simulate processing with small delays to get realistic timing
        for chunk in scenario["chunks"]:
            observer.feed_chunk(chunk)
            time.sleep(0.01)  # Small delay for timing

        elapsed = time.time() - start_time
        metrics = observer.finalize_metrics()

        # Display metrics
        f.subheader("METRICS")
        f.metadata("Total Processing Time", f"{elapsed:.4f}s")
        f.metadata("Total Segments", str(metrics.total_segments))
        f.print()

        f.subheader("THINKING METRICS")
        f.metadata("Thinking Duration", f"{metrics.thinking_duration:.4f}s")
        f.metadata("Thinking Token Count (est.)", str(metrics.thinking_token_count))
        f.metadata("Thinking Segments", str(metrics.thinking_segments))
        f.print()

        f.subheader("ANSWER METRICS")
        f.metadata("Answer Duration", f"{metrics.answer_duration:.4f}s")
        f.metadata("Answer Token Count (est.)", str(metrics.answer_token_count))
        f.metadata("Answer Segments", str(metrics.answer_segments))
        f.print()

        f.subheader("COMPARATIVE ANALYSIS")
        total_mode_time = metrics.thinking_duration + metrics.answer_duration
        if total_mode_time > 0:
            thinking_pct = (metrics.thinking_duration / total_mode_time) * 100
            answer_pct = (metrics.answer_duration / total_mode_time) * 100
            f.script(f"  Thinking ratio: {thinking_pct:.1f}%")
            f.script(f"  Answer ratio:   {answer_pct:.1f}%")
        f.script(f"  Mode switches:  {metrics.mode_switches}")
        f.print()

        # Insights
        f.subheader("INSIGHTS")
        if metrics.thinking_duration > metrics.answer_duration:
            f.script("  This model spent more time thinking than answering,")
            f.script("  suggesting deep reasoning was required.")
        elif metrics.answer_duration > metrics.thinking_duration:
            f.script("  The model answered quickly with minimal thinking,")
            f.script("  suggesting a straightforward question.")
        else:
            f.script("  Thinking and answer times were roughly balanced.")
        
        if metrics.mode_switches > 2:
            f.script(f"  High mode switches ({metrics.mode_switches}) indicate")
            f.script("  the model reconsidered its approach mid-response.")
        f.print()

        print("-" * 60)
        f.print()

    # Summary
    f.subheader("WHY THINKING METRICS MATTER")
    f.script("  Understanding thinking vs answer patterns provides insights:")
    f.script("  - Thinking duration correlates with problem complexity")
    f.script("  - Mode switches indicate self-correction behavior")
    f.script("  - Token counts help estimate API costs")
    f.script("  - Response patterns reveal model reasoning styles")
    f.script("  - Metrics can be used to optimize prompt engineering")
    f.print()


if __name__ == "__main__":
    demo_thinking_metrics()