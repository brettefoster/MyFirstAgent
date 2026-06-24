#!/usr/bin/env python3
"""
Central Configuration Module

This module provides a single source of truth for API configuration.
All scripts and modules should import from here instead of reading .env directly.

Configuration is loaded from the .env file via python-dotenv, with sensible defaults.

Usage:
    from utils.config import config

    print(config.api_base)    # e.g. "http://localhost:8080"
    print(config.model)        # e.g. "llama3"
    print(config.api_key)      # e.g. "ollama"
"""

import os
from dotenv import load_dotenv
from pathlib import Path


class Config:
    """
    Central configuration loaded from .env file.

    Attributes:
        api_base: Base URL of the OpenAI-compatible API (no trailing slash, no /v1 suffix).
        model: Default model name to use for completions.
        api_key: API key (may not be required for local deployments).
    """

    def __init__(self):
        # Load .env from project root (parent of utils/)
        project_root = Path(__file__).resolve().parent.parent
        load_dotenv(project_root / ".env")

        self.api_base: str = os.getenv("API_BASE", "http://localhost:8080").rstrip("/")
        self.model: str = os.getenv("MODEL", "llama3")
        self.api_key: str = os.getenv("API_KEY", "ollama")
        self.context_window_size: int = int(os.getenv("CONTEXT_WINDOW_SIZE", "64000"))
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))

    def summary(self) -> str:
        """Return a human-readable summary of the configuration."""
        key_display = "*" * 5 if self.api_key and self.api_key != "ollama" else "(not required)"
        return (
            f"  API Base:            {self.api_base}\n"
            f"  Model:                 {self.model}\n"
            f"  API Key:               {key_display}\n"
            f"  Context Window Size:   {self.context_window_size}\n"
            f"  Max Tokens:            {self.max_tokens}"
        )


# Singleton instance - loaded once on first import
config = Config()