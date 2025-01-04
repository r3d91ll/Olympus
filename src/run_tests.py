#!/usr/bin/env python3
"""Test runner script for the Olympus project.

This script provides a convenient way to run tests with different configurations
and generate coverage reports.
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_tests(args: argparse.Namespace) -> int:
    """Run the tests with the specified configuration.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code from pytest
    """
    pytest_args = [
        "pytest",
        "--verbose",
        f"--cov={args.source}",
        "--cov-report=term-missing",
    ]
    
    if args.html_report:
        pytest_args.append("--cov-report=html")
    
    if args.junit_report:
        pytest_args.append("--junitxml=test-results.xml")
    
    if args.test_type:
        pytest_args.extend(["-m", args.test_type])
    
    if args.parallel:
        pytest_args.extend(["-n", "auto"])
    
    if args.failfast:
        pytest_args.append("-x")
    
    if args.pattern:
        pytest_args.append(args.pattern)
    else:
        pytest_args.append("tests/")
    
    return subprocess.call(pytest_args)

def main() -> int:
    """Main entry point for the test runner.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="Run tests for the Olympus project"
    )
    
    parser.add_argument(
        "--source",
        default="src_new",
        help="Source directory to measure coverage for"
    )
    
    parser.add_argument(
        "--test-type",
        choices=["unit", "integration"],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--junit-report",
        action="store_true",
        help="Generate JUnit XML report"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--failfast",
        action="store_true",
        help="Stop on first failure"
    )
    
    parser.add_argument(
        "pattern",
        nargs="?",
        help="Pattern to match test files"
    )
    
    args = parser.parse_args()
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main())
