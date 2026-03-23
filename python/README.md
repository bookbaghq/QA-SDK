# Bookbag Python SDK

Zero-dependency Python SDK for the Bookbag Decision Gate API.

## Install

```bash
pip install ./sdk/python
```

## Quick Start

```python
from bookbag import BookbagClient

client = BookbagClient(
    api_key="bk_gate_YOUR_KEY_HERE",
    base_url="https://your-bookbag-instance.com"
)

result = client.gate.evaluate(
    input="Customer asks for refund",
    output="You are eligible for a full refund within 30 days."
)

print(result.decision)       # "allow", "flag", or "block"
print(result.risk)           # "low", "medium", or "high"
print(result.policy_action)  # "allow", "review", "block", "require_sme"
print(result.flags)          # ["hallucination", ...] or []
print(result.audit_id)       # Unique audit trail ID

if result.policy_action == "block":
    prevent_send()
elif result.policy_action == "review":
    queue_for_review(result)
else:
    send_response()
```

## Error Handling

```python
from bookbag.exceptions import AuthenticationError, RateLimitError, InsufficientCreditsError

try:
    result = client.gate.evaluate(input="...", output="...")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited — retry after {e.reset_time}")
except InsufficientCreditsError:
    print("Out of credits")
```

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib `urllib`)
