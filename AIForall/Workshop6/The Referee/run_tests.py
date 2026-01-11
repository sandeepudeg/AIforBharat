#!/usr/bin/env python3.13
"""Simple test runner."""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/properties/test_constraint_properties.py", "-v", "--tb=short"],
    cwd="The Referee"
)
sys.exit(result.returncode)
