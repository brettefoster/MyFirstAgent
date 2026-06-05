#!/usr/bin/env python3
"""
Stage 5: The Reflection Loop

This module implements loop detection, backtracking, and retry mechanisms
for the agent execution loop.

Run with: python loop_detector.py
"""

import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class ExecutionStep:
    """Represents a single step in the agent execution."""
    step_number: int
    action: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class LoopDetectionResult:
    """Result of loop detection analysis."""
    is_loop: bool
    loop_start: int
    loop_length: int
    confidence: float
    pattern: str


class LoopDetector:
    """
    Detects infinite loops in agent execution.
    
    The detector uses multiple strategies:
    1. Exact match detection - Same action with same inputs
    2. Semantic similarity - Similar actions with similar inputs
    3. Pattern detection - Repeating sequences of actions
    """
    
    def __init__(self, window_size: int = 10, similarity_threshold: float = 0.8):
        """
        Initialize the loop detector.
        
        Args:
            window_size: Number of recent steps to analyze.
            similarity_threshold: Threshold for semantic similarity (0-1).
        """
        self.window_size = window_size
        self.similarity_threshold = similarity_threshold
        self.history: deque = deque(maxlen=window_size)
    
    def add_step(self, step: ExecutionStep) -> None:
        """
        Add a new execution step to the history.
        
        Args:
            step: The step to add.
        """
        self.history.append(step)
    
    def detect_loop(self) -> LoopDetectionResult:
        """
        Analyze the history for loop patterns.
        
        Returns:
            LoopDetectionResult with analysis findings.
        """
        if len(self.history) < 2:
            return LoopDetectionResult(
                is_loop=False,
                loop_start=0,
                loop_length=0,
                confidence=0.0,
                pattern=""
            )
        
        steps = list(self.history)
        
        # Strategy 1: Exact match detection
        exact_result = self._detect_exact_loops(steps)
        if exact_result.is_loop:
            return exact_result
        
        # Strategy 2: Pattern detection (repeating sequences)
        pattern_result = self._detect_pattern_loops(steps)
        if pattern_result.is_loop:
            return pattern_result
        
        return LoopDetectionResult(
            is_loop=False,
            loop_start=0,
            loop_length=0,
            confidence=0.0,
            pattern=""
        )
    
    def _detect_exact_loops(self, steps: List[ExecutionStep]) -> LoopDetectionResult:
        """Detect exact repeating steps."""
        n = len(steps)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Check if steps are identical
                if self._steps_are_identical(steps[i], steps[j]):
                    loop_length = j - i
                    confidence = self._calculate_confidence(i, j, steps)
                    
                    return LoopDetectionResult(
                        is_loop=True,
                        loop_start=i,
                        loop_length=loop_length,
                        confidence=confidence,
                        pattern=f"Step {i} repeats at step {j}"
                    )
        
        return LoopDetectionResult(
            is_loop=False,
            loop_start=0,
            loop_length=0,
            confidence=0.0,
            pattern=""
        )
    
    def _detect_pattern_loops(self, steps: List[ExecutionStep]) -> LoopDetectionResult:
        """Detect repeating patterns of steps."""
        n = len(steps)
        
        # Check for patterns of length 2, 3, 4, etc.
        for pattern_len in range(2, min(n // 2, 5)):
            pattern = steps[-pattern_len:]
            
            # Check if this pattern repeats
            if n >= 2 * pattern_len:
                previous = steps[-2 * pattern_len:-pattern_len]
                
                if self._patterns_are_similar(pattern, previous):
                    return LoopDetectionResult(
                        is_loop=True,
                        loop_start=n - 2 * pattern_len,
                        loop_length=pattern_len,
                        confidence=0.9,
                        pattern=f"Pattern of {pattern_len} steps repeats"
                    )
        
        return LoopDetectionResult(
            is_loop=False,
            loop_start=0,
            loop_length=0,
            confidence=0.0,
            pattern=""
        )
    
    def _steps_are_identical(self, step1: ExecutionStep, step2: ExecutionStep) -> bool:
        """Check if two steps are identical."""
        if step1.action != step2.action:
            return False
        
        # Compare inputs
        if step1.input_data != step2.input_data:
            return False
        
        return True
    
    def _patterns_are_similar(self, pattern1: List[ExecutionStep], 
                               pattern2: List[ExecutionStep]) -> bool:
        """Check if two patterns of steps are similar."""
        if len(pattern1) != len(pattern2):
            return False
        
        for s1, s2 in zip(pattern1, pattern2):
            if s1.action != s2.action:
                return False
        
        return True
    
    def _calculate_confidence(self, i: int, j: int, steps: List[ExecutionStep]) -> float:
        """Calculate confidence score for loop detection."""
        # Base confidence from repetition count
        repetition_count = 2  # We found 2 repetitions
        
        # Bonus for longer loops
        loop_length = j - i
        length_bonus = min(loop_length / 10, 0.2)
        
        # Bonus for recent loops
        recency_bonus = 0.1 if j == len(steps) - 1 else 0.0
        
        return min(0.5 + repetition_count * 0.2 + length_bonus + recency_bonus, 1.0)
    
    def get_history_summary(self) -> str:
        """Get a summary of the execution history."""
        if not self.history:
            return "No execution history."
        
        lines = ["Execution History:"]
        for step in self.history:
            status = "✓" if step.success else "✗"
            lines.append(f"  {step.step_number}. [{status}] {step.action}")
        
        return "\n".join(lines)


class Backtracker:
    """
    Manages backtracking and retry logic for failed steps.
    
    The backtracker:
    1. Identifies the point of failure
    2. Generates alternative approaches
    3. Implements exponential backoff for rate limits
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize the backtracker.
        
        Args:
            max_retries: Maximum number of retry attempts.
        """
        self.max_retries = max_retries
        self.retry_counts: Dict[str, int] = {}
    
    def should_retry(self, step_key: str) -> bool:
        """
        Check if a step should be retried.
        
        Args:
            step_key: Unique identifier for the step.
            
        Returns:
            True if retry is allowed.
        """
        current_count = self.retry_counts.get(step_key, 0)
        return current_count < self.max_retries
    
    def record_retry(self, step_key: str) -> int:
        """
        Record a retry attempt.
        
        Args:
            step_key: Unique identifier for the step.
            
        Returns:
            Current retry count.
        """
        count = self.retry_counts.get(step_key, 0) + 1
        self.retry_counts[step_key] = count
        return count
    
    def get_backoff_delay(self, step_key: str) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            step_key: Unique identifier for the step.
            
        Returns:
            Delay in seconds.
        """
        count = self.retry_counts.get(step_key, 0)
        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        return min(2 ** count, 30)  # Max 30 seconds
    
    def generate_alternative(self, failed_step: ExecutionStep) -> Dict[str, Any]:
        """
        Generate an alternative approach for a failed step.
        
        Args:
            failed_step: The step that failed.
            
        Returns:
            Alternative input data for retry.
        """
        alternative = failed_step.input_data.copy()
        
        # Add context about the failure
        alternative["_retry_context"] = {
            "original_error": failed_step.error,
            "attempt": self.retry_counts.get(failed_step.action, 0) + 1,
            "suggestion": "Try a different approach or simplify the request"
        }
        
        return alternative


class ErrorFormatter:
    """
    Formats errors as context for the LLM.
    
    This helps the LLM understand what went wrong and how to fix it.
    """
    
    @staticmethod
    def format_error(step: ExecutionStep) -> str:
        """
        Format a failed step as context for the LLM.
        
        Args:
            step: The failed execution step.
            
        Returns:
            Formatted error message.
        """
        lines = [
            f"ERROR in step {step.step_number}: {step.action}",
            f"Input: {step.input_data}",
            f"Error: {step.error}",
            "",
            "Suggestion: Review the error and try a different approach."
        ]
        return "\n".join(lines)
    
    @staticmethod
    def format_success(step: ExecutionStep) -> str:
        """
        Format a successful step as context for the LLM.
        
        Args:
            step: The successful execution step.
            
        Returns:
            Formatted success message.
        """
        return f"Step {step.step_number} ({step.action}) completed successfully."


def demo_loop_detector():
    """Demonstrate loop detection functionality."""
    print("\n" + "=" * 60)
    print("STAGE 5: THE REFLECTION LOOP")
    print("Loop Detection and Backtracking")
    print("=" * 60 + "\n")
    
    detector = LoopDetector(window_size=10)
    
    # Simulate an execution with a loop
    print("SIMULATING EXECUTION WITH LOOP:")
    print("-" * 60)
    
    steps = [
        ExecutionStep(1, "search", {"query": "Python"}, {"results": [...]}, True),
        ExecutionStep(2, "analyze", {"data": "results"}, {"analysis": "..."}, True),
        ExecutionStep(3, "search", {"query": "Python tutorials"}, {"results": [...]}, True),
        ExecutionStep(4, "analyze", {"data": "tutorials"}, {"analysis": "..."}, True),
        ExecutionStep(5, "search", {"query": "Python"}, {"results": [...]}, True),  # Loop!
        ExecutionStep(6, "analyze", {"data": "results"}, {"analysis": "..."}, True),  # Loop!
    ]
    
    for step in steps:
        detector.add_step(step)
        print(f"Added step {step.step_number}: {step.action}")
    
    print("\n" + "-" * 60)
    print("LOOP DETECTION ANALYSIS:")
    print("-" * 60)
    
    result = detector.detect_loop()
    print(f"Is loop detected: {result.is_loop}")
    if result.is_loop:
        print(f"Loop starts at step: {result.loop_start}")
        print(f"Loop length: {result.loop_length}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Pattern: {result.pattern}")
    
    print("\n" + detector.get_history_summary())


def demo_backtracker():
    """Demonstrate backtracking functionality."""
    print("\n" + "=" * 60)
    print("BACKTRACKING DEMO")
    print("=" * 60 + "\n")
    
    backtracker = Backtracker(max_retries=3)
    
    # Simulate retries
    step_key = "search_query"
    
    print(f"Simulating retries for step: {step_key}")
    print("-" * 60)
    
    for i in range(5):
        if backtracker.should_retry(step_key):
            count = backtracker.record_retry(step_key)
            delay = backtracker.get_backoff_delay(step_key)
            print(f"  Retry {count}: Will wait {delay}s before next attempt")
        else:
            print(f"  Max retries ({backtracker.max_retries}) exceeded. Giving up.")
            break


def demo_error_formatting():
    """Demonstrate error formatting."""
    print("\n" + "=" * 60)
    print("ERROR FORMATTING DEMO")
    print("=" * 60 + "\n")
    
    failed_step = ExecutionStep(
        step_number=3,
        action="search",
        input_data={"query": "nonexistent website"},
        output_data={},
        success=False,
        error="Connection timeout: Could not reach website"
    )
    
    print("FORMATTED ERROR FOR LLM:")
    print("-" * 60)
    print(ErrorFormatter.format_error(failed_step))
    
    print("\n" + "-" * 60)
    print("SUCCESS MESSAGE:")
    print("-" * 60)
    
    success_step = ExecutionStep(
        step_number=4,
        action="analyze",
        input_data={"data": "fetched content"},
        output_data={"summary": "Analysis complete"},
        success=True
    )
    print(ErrorFormatter.format_success(success_step))


if __name__ == "__main__":
    demo_loop_detector()
    demo_backtracker()
    demo_error_formatting()