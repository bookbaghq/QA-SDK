#!/usr/bin/env python3
"""
Gate API Test Suite (Python SDK)

Tests the Gate API using the Python SDK.

Usage:
    python sdk/tests/test_gate_api.py [api_key] [base_url]

Prerequisites:
    - Server running at base_url
    - A valid gate API key for an automated project
"""

import sys
import os
import json

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from bookbag import BookbagClient
from bookbag.exceptions import BookbagError, AuthenticationError, RateLimitError

API_KEY = sys.argv[1] if len(sys.argv) > 1 else 'bk_gate_YOUR_KEY_HERE'
BASE_URL = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8080'

passed = 0
failed = 0
skipped = 0

def log(icon, msg):
    print(f"{icon} {msg}")

def test_pass(name):
    global passed
    passed += 1
    log("✅", name)

def test_fail(name, reason):
    global failed
    failed += 1
    log("❌", f"{name}: {reason}")

def test_skip(name, reason):
    global skipped
    skipped += 1
    log("⏭️", f"{name}: {reason}")


def test_invalid_key():
    """Test that invalid API key raises AuthenticationError."""
    try:
        client = BookbagClient(api_key="bk_gate_invalid", base_url=BASE_URL)
        client.gate.evaluate(input="test", output="test")
        test_fail("Invalid key", "Should have raised AuthenticationError")
    except AuthenticationError:
        test_pass("Invalid key raises AuthenticationError")
    except Exception as e:
        # Connection error means server isn't running
        if "Connection" in str(e) or "urlopen" in str(e):
            test_skip("Invalid key", f"Server not reachable: {e}")
        else:
            test_fail("Invalid key", str(e))


def test_missing_key():
    """Test that missing API key raises error."""
    try:
        BookbagClient(api_key="")
        test_fail("Missing key", "Should have raised error")
    except AuthenticationError:
        test_pass("Missing key raises AuthenticationError")


def test_evaluate():
    """Test evaluation with valid key."""
    if API_KEY == 'bk_gate_YOUR_KEY_HERE':
        test_skip("Evaluate", "No API key provided")
        return

    client = BookbagClient(api_key=API_KEY, base_url=BASE_URL)

    # Load test data
    test_data_path = os.path.join(os.path.dirname(__file__), 'gate_test_data.json')
    with open(test_data_path) as f:
        test_cases = json.load(f)['test_cases']

    for tc in test_cases[:3]:  # Test first 3 cases
        try:
            result = client.gate.evaluate(
                input=tc['input'],
                output=tc['output'],
                context=tc.get('context', {}),
                metadata=tc.get('metadata', {})
            )

            # Validate response structure
            assert result.decision in ('allow', 'flag', 'block', 'queued'), f"Bad decision: {result.decision}"
            assert result.audit_id, "Missing audit_id"
            assert result.policy_action in ('allow', 'review', 'block', 'require_sme', 'allow_with_warning', 'queued'), f"Bad policy_action: {result.policy_action}"

            icon = '🟢' if result.decision == 'allow' else '🔴' if result.decision == 'block' else '🟡'
            log(icon, f"  {tc['name']}: decision={result.decision} risk={result.risk} action={result.policy_action} confidence={result.confidence}")
            test_pass(f"Evaluate: {tc['name']}")

        except BookbagError as e:
            if 'taxonomy' in str(e).lower() or 'model' in str(e).lower():
                test_skip(f"Evaluate: {tc['name']}", f"Project setup: {e}")
            else:
                test_fail(f"Evaluate: {tc['name']}", str(e))
        except Exception as e:
            if "Connection" in str(e) or "urlopen" in str(e):
                test_skip(f"Evaluate: {tc['name']}", "Server not reachable")
                break
            else:
                test_fail(f"Evaluate: {tc['name']}", str(e))


def test_sdk_result_object():
    """Test GateResult dataclass."""
    from bookbag.gate import GateResult

    result = GateResult(
        decision="allow",
        risk="low",
        flags=[],
        policy_action="allow",
        enforced=False,
        audit_id="test_123",
        task_id=1,
        confidence=0.95,
        scores={"correctness": 5},
        rationale="Looks good",
        evaluation_ms=1234
    )

    assert result.decision == "allow"
    assert result.risk == "low"
    assert result.confidence == 0.95
    assert result.audit_id == "test_123"
    assert result.evaluation_ms == 1234
    test_pass("GateResult dataclass")


def main():
    print(f"\n🐍 Bookbag Gate API Python SDK Tests")
    print(f"   Base URL: {BASE_URL}")
    print(f"   API Key: {API_KEY[:16]}..." if len(API_KEY) > 16 else f"   API Key: {API_KEY}")
    print()

    # Unit tests (no server needed)
    test_missing_key()
    test_sdk_result_object()
    print()

    # Integration tests (need server)
    test_invalid_key()
    print()

    # Evaluation tests (need server + project + LLM)
    test_evaluate()
    print()

    # Summary
    print("========== Results ==========")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️ Skipped: {skipped}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
