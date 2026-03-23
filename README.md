# Bookbag Decision Gate SDK

Real-time AI output evaluation. Sits between your AI and your users — evaluates, scores, and gates AI decisions before they execute.

## How It Works

```
Your AI produces output
    → Send to Bookbag Gate API
    → Bookbag evaluates using your project's taxonomy + model
    → Returns: decision (allow/flag/block) + risk + flags + policy_action
    → Your app acts on the result
    → Full audit trail stored automatically
```

## Quick Start

### 1. Create a Project

In the Bookbag admin, create a project with:
- A taxonomy template (what to evaluate — hallucination, tone, compliance, etc.)
- A model (which LLM evaluates — use a small/fast model for cost efficiency)
- Review mode: `automated` for real-time decisions

### 2. Get an API Key

Go to your project's **Gate API** tab → Create Key → copy the key.

### 3. Install the SDK

**Python:**
```bash
pip install ./sdk/python
```

**Node.js:**
```bash
npm install ./sdk/node
```

### 4. Evaluate

**Python:**
```python
from bookbag import BookbagClient

client = BookbagClient(api_key="bk_gate_xxx", base_url="https://your-bookbag.com")

result = client.gate.evaluate(
    input="What is my balance?",
    output="Your balance is $5,230."
)

if result.policy_action == "block":
    # Do not send — critical issues
    pass
elif result.policy_action == "review":
    # Flag for review
    queue_for_review(result)
else:
    # Safe to send
    send_response(output)
```

**Node.js:**
```javascript
const { BookbagClient } = require('@bookbag/sdk');

const client = new BookbagClient({ apiKey: 'bk_gate_xxx', baseUrl: 'https://your-bookbag.com' });

const result = await client.gate.evaluate({
    input: 'What is my balance?',
    output: 'Your balance is $5,230.'
});

if (result.policy_action === 'block') { /* block */ }
else if (result.policy_action === 'review') { /* flag */ }
else { /* allow */ }
```

**cURL:**
```bash
curl -X POST https://your-bookbag.com/api/v1/gate/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bk_gate_xxx" \
  -d '{"input":"What is my balance?","output":"Your balance is $5,230."}'
```

## Response Format

```json
{
  "decision": "flag",
  "risk": "medium",
  "flags": ["hallucination"],
  "policy_action": "review",
  "enforced": false,
  "audit_id": "gate_eval_456_789",
  "task_id": 456,
  "confidence": 0.82,
  "scores": { "correctness_score": 3, "tone_score": 5 },
  "rationale": "Refund timeframe appears unsupported by policy.",
  "evaluation_ms": 2340
}
```

| Field | Description |
|---|---|
| `decision` | What Bookbag thinks: `allow`, `flag`, or `block` |
| `risk` | Risk level: `low`, `medium`, or `high` |
| `flags` | Triggered failure categories (hallucination, tone_issue, etc.) |
| `policy_action` | What your app should do: `allow`, `review`, `block`, `require_sme` |
| `enforced` | `true` if your project uses enforced mode |
| `audit_id` | Unique ID for compliance/audit trail |
| `task_id` | Task ID in Bookbag (visible in project Tasks tab) |
| `confidence` | AI confidence score (0-1) |
| `scores` | Taxonomy scores (rubric scores from your template) |
| `rationale` | AI explanation of the decision |
| `evaluation_ms` | How long the evaluation took in milliseconds |

## Review Modes

| Mode | Behavior |
|---|---|
| `automated` | AI evaluates immediately, returns decision. No human involvement. |
| `human` | Task queued for human reviewer. Returns `decision: "queued"`. |
| `assisted` | AI evaluates and returns decision immediately. Human review happens async for training data. |

## Policy

Configure policies in the **Policy** tab of your project to control:
- **Routing:** Where tasks go based on verdict (auto-complete, annotator, QA, SME)
- **Risk escalation:** Override routing based on risk level
- **Flag rules:** Escalate based on specific failure categories
- **Auto-approval:** Automatically approve high-confidence, low-risk results
- **Export rules:** Control what data goes into training exports
- **Enforcement:** Advisory (your app decides) vs Enforced (obey policy_action)

## SDKs

- **Python:** `sdk/python/` — zero dependencies, uses stdlib `urllib`
- **Node.js:** `sdk/node/` — zero dependencies, uses native `fetch`

## Examples

- `sdk/python/examples/basic_gate.py` — Simple evaluation
- `sdk/python/examples/error_handling.py` — Graceful error handling
- `sdk/node/examples/basic_gate.js` — Simple evaluation
- `sdk/node/examples/express_middleware.js` — Express middleware for automatic gating
