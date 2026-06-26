#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 4: Exponential Backoff

This script demonstrates implementing exponential backoff for rate limits
and transient failures, with configurable base delay and max delay.
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


class RateLimitHandler:
    """Handles rate limiting with exponential backoff strategy."""

    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_count = 0

    def get_delay(self) -> float:
        """Calculate delay with exponential backoff."""
        delay = min(self.base_delay * (2 ** self.retry_count), self.max_delay)
        return delay

    def wait_and_retry(self) -> float:
        """Wait and prepare for retry. Returns the delay used."""
        delay = self.get_delay()
        self.retry_count += 1
        return delay

    def reset(self):
        """Reset retry count after success."""
        self.retry_count = 0

    @property
    def current_delay(self) -> float:
        """Get the next delay without incrementing counter."""
        return self.get_delay()


def demo_exponential_backoff():
    """Demonstrate exponential backoff behavior with different configurations."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 4: EXPONENTIAL BACKOFF")
    f.script("Implementing Backoff for Rate Limits")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    f.subheader("CONFIGURATION 1: AGGRESSIVE BACKOFF")
    f.script("  base_delay=0.5s, max_delay=10.0s")
    f.print()

    aggressive_handler = RateLimitHandler(base_delay=0.5, max_delay=10.0)
    _simulate_retries(f, aggressive_handler, "AGGRESSIVE", simulate_time=False)

    f.print()

    f.subheader("CONFIGURATION 2: STANDARD BACKOFF")
    f.script("  base_delay=1.0s, max_delay=60.0s")
    f.print()

    standard_handler = RateLimitHandler(base_delay=1.0, max_delay=60.0)
    _simulate_retries(f, standard_handler, "STANDARD", simulate_time=False)

    f.print()

    f.subheader("CONFIGURATION 3: CONSERVATIVE BACKOFF")
    f.script("  base_delay=2.0s, max_delay=120.0s")
    f.print()

    conservative_handler = RateLimitHandler(base_delay=2.0, max_delay=120.0)
    _simulate_retries(f, conservative_handler, "CONSERVATIVE", simulate_time=False)

    # Summary
    f.subheader("DELAY COMPARISON TABLE")
    f.script("  Retry# | Aggressive | Standard  | Conservative")
    f.script("  " + "-" * 55)
    for i in range(8):
        delay = min(0.5 * (2 ** i), 10.0)
        delay_s = min(1.0 * (2 ** i), 60.0)
        delay_c = min(2.0 * (2 ** i), 120.0)
        f.script(f"    {i+1:4d} |    {delay:6.1f}s  |   {delay_s:5.1f}s  |   {delay_c:6.1f}s")
    f.print()

    f.subheader("EXERCISE ANSWER")
    f.script("  Question: What are good values for base_delay and max_delay?")
    f.script("")
    f.script("  base_delay:")
    f.script("    - 0.5-1.0s: Good for local/dev servers with light load")
    f.script("    - 1.0-2.0s: Good default for most APIs")
    f.script("    - 2.0-5.0s: For strict rate-limited production APIs")
    f.script("")
    f.script("  max_delay:")
    f.script("    - 10-30s: Short sessions, quick recovery expected")
    f.script("    - 60s: Standard for most use cases")
    f.script("    - 120s+: For very strict rate limits")
    f.script("")
    f.script("  Key Insight:")
    f.script("  - Exponential backoff prevents overwhelming the API")
    f.script("  - The cap (max_delay) prevents unbounded waiting")
    f.script("  - Reset after success prevents accumulated delays")


def _simulate_retries(f: Formatter, handler: RateLimitHandler, label: str, simulate_time: bool = False):
    """Simulate multiple retry attempts and display the backoff behavior."""
    f.script(f"  Simulating {label} backoff ({handler.retry_count} retries initially)...")
    f.print()

    max_retries = 6

    for i in range(max_retries):
        delay = handler.wait_and_retry()

        if simulate_time:
            f.script(f"  Retry {i+1}: Waiting {delay:.1f}s...")
            time.sleep(min(delay, 0.1))  # Cap actual wait for demo
        else:
            f.script(f"  Retry {i+1}: Would wait {delay:.1f}s (simulated)")

    f.script(f"  Final retry count: {handler.retry_count}")
    f.script(f"  Next delay if retried again: {handler.current_delay:.1f}s")
    f.script(f"  (Capped at max_delay: {handler.max_delay}s)")


if __name__ == "__main__":
    demo_exponential_backoff()