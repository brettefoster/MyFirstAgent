#!/usr/bin/env python3
"""
Compile Validation Script

Recursively finds all Python files in the project and verifies they compile
without syntax errors.

Usage:
    python scripts/validate.py
"""

import os
import sys
import py_compile
from pathlib import Path


def find_python_files(root: str) -> list[str]:
    """Recursively find all .py files, excluding __pycache__ directories."""
    py_files = []
    for dirpath, _dirnames, filenames in os.walk(root):
        # Skip __pycache__ and .venv directories
        if "__pycache__" in dirpath or ".venv" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                py_files.append(os.path.join(dirpath, filename))
    return sorted(py_files)


def validate_compilation(files: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """
    Validate that all Python files compile without errors.
    
    Returns:
        Tuple of (successful_files, failed_files_with_errors)
    """
    successful = []
    failed = []
    
    for filepath in files:
        try:
            py_compile.compile(filepath, doraise=True)
            successful.append(filepath)
            print(f"  OK: {filepath}")
        except py_compile.PyCompileError as e:
            failed.append((filepath, str(e)))
            print(f"FAIL: {filepath}")
            print(f"      {e}")
    
    return successful, failed


def main() -> int:
    """Main entry point."""
    project_root = Path(__file__).resolve().parent.parent
    print(f"\nValidating Python files in: {project_root}")
    print("=" * 60)
    
    files = find_python_files(str(project_root))
    
    if not files:
        print("No Python files found!")
        return 1
    
    print(f"Found {len(files)} Python file(s)\n")
    
    successful, failed = validate_compilation(files)
    
    print("=" * 60)
    print(f"\nResults:")
    print(f"  Passed: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    
    if failed:
        print(f"\n{len(failed)} file(s) failed to compile!")
        return 1
    else:
        print(f"\nAll {len(successful)} Python files compile successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())