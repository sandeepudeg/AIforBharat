#!/usr/bin/env python3
"""Basic test to verify the constraint parser works."""

from src.models import Constraint
from src.constraint_parser import ConstraintParser

# Test 1: Valid constraint
print("=" * 60)
print("TEST 1: Valid Constraint Parsing")
print("=" * 60)

raw_inputs = {
    "data_structure": "Relational",
    "read_write_ratio": 50,
    "consistency_level": "Strong",
    "query_complexity": "Complex",
    "scale_gb": 10.0,
    "latency_ms": 5.0,
    "team_expertise": "Medium",
    "requires_persistence": True,
}

constraint, error = ConstraintParser.parse_constraints(raw_inputs)

if error:
    print(f"❌ Error: {error.message}")
else:
    print("✅ Constraint parsed successfully!")
    print(f"   Data Structure: {constraint.data_structure}")
    print(f"   Read/Write Ratio: {constraint.read_write_ratio}%")
    print(f"   Consistency Level: {constraint.consistency_level}")
    print(f"   Query Complexity: {constraint.query_complexity}")
    print(f"   Scale: {constraint.scale_gb} GB")
    print(f"   Latency: {constraint.latency_ms} ms")
    print(f"   Team Expertise: {constraint.team_expertise}")
    print(f"   Persistence Required: {constraint.requires_persistence}")

# Test 2: Invalid constraint (out of range)
print("\n" + "=" * 60)
print("TEST 2: Invalid Constraint (Out of Range)")
print("=" * 60)

invalid_inputs = {
    "data_structure": "Relational",
    "read_write_ratio": 150,  # Invalid: > 100
    "consistency_level": "Strong",
    "query_complexity": "Complex",
    "scale_gb": 10.0,
    "latency_ms": 5.0,
    "team_expertise": "Medium",
}

constraint, error = ConstraintParser.parse_constraints(invalid_inputs)

if error:
    print(f"✅ Correctly rejected: {error.message}")
else:
    print("❌ Should have been rejected!")

# Test 3: Invalid data structure
print("\n" + "=" * 60)
print("TEST 3: Invalid Data Structure")
print("=" * 60)

invalid_inputs = {
    "data_structure": "InvalidType",  # Invalid
    "read_write_ratio": 50,
    "consistency_level": "Strong",
    "query_complexity": "Complex",
    "scale_gb": 10.0,
    "latency_ms": 5.0,
    "team_expertise": "Medium",
}

constraint, error = ConstraintParser.parse_constraints(invalid_inputs)

if error:
    print(f"✅ Correctly rejected: {error.message}")
else:
    print("❌ Should have been rejected!")

print("\n" + "=" * 60)
print("All basic tests completed!")
print("=" * 60)
