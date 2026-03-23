# Bookbag QA SDK

Real-time AI output evaluation. Sits between your AI and your users — evaluates, scores, and gates every response before it ships.

```
Your AI generates a response
    → Bookbag evaluates it against your taxonomy (hallucination, tone, compliance, etc.)
    → Returns a decision: allow, flag, or block
    → Your app enforces the decision
    → Full audit trail stored automatically
```

Available for **Python** and **Node.js**. Zero external dependencies.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [How the Gate Works](#how-the-gate-works)
- [API Reference](#api-reference)
  - [Client](#client)
  - [gate.evaluate()](#gateevaluate)
  - [Response Object](#response-object)
- [Response Fields — Deep Dive](#response-fields--deep-dive)
- [Review Modes](#review-modes)
- [Evaluation Depth](#evaluation-depth)
- [Policy System](#policy-system)
- [Error Handling](#error-handling)
- [Integration Patterns](#integration-patterns)
  - [Basic Gating](#basic-gating)
  - [Express Middleware](#express-middleware)
  - [FastAPI Middleware](#fastapi-middleware)
  - [Async Processing](#async-processing)
- [Architecture](#architecture)
- [Credits and Billing](#credits-and-billing)

---

## Installation

**Python** (3.8+, zero dependencies):
```bash
pip install bookbag
```

**Node.js** (18+, zero dependencies):
```bash
npm install @bookbag/sdk
```

---

## Quick Start

### Prerequisites

1. **Create a project** in the Bookbag admin dashboard
2. **Select a taxonomy template** — defines what gets evaluated (hallucination, tone, policy violations, etc.)
3. **Assign a model** — the LLM that performs the evaluation
4. **Set review mode** — `automated` for real-time decisions
5. **Generate an API key** — project settings > Gate API tab > Create Key

### Python

```python
from bookbag import BookbagClient

client = BookbagClient(api_key="bk_gate_xxx")

result = client.gate.evaluate(
    input="What is my refund policy?",
    output="You can get a full refund within 90 days, no questions asked.",
    context={"channel": "support_chat"},
    metadata={"session_id": "s_abc123", "model": "gpt-4o-mini"}
)

if result.policy_action == "block":
    fallback_response()          # Critical issue — don't send
elif result.policy_action == "review":
    send_with_flag(result)       # Minor issue — send but flag for review
elif result.policy_action == "require_sme":
    escalate_to_expert(result)   # Needs expert review before proceeding
else:
    send_response(output)        # Safe to send

print(f"Decision: {result.decision}")        # "allow", "flag", or "block"
print(f"Confidence: {result.confidence}")     # 0.0 — 1.0
print(f"Flags: {result.flags}")              # ["hallucination", "policy_violation"]
print(f"Eval time: {result.evaluation_ms}ms") # Latency
```

### Node.js

```javascript
const { BookbagClient } = require('@bookbag/sdk');

const client = new BookbagClient({ apiKey: 'bk_gate_xxx' });

const result = await client.gate.evaluate({
    input: 'What is my refund policy?',
    output: 'You can get a full refund within 90 days, no questions asked.',
    context: { channel: 'support_chat' },
    metadata: { session_id: 's_abc123', model: 'gpt-4o-mini' }
});

switch (result.policy_action) {
    case 'block':    /* Critical — don't send */ break;
    case 'review':   /* Flag for human review */ break;
    case 'require_sme': /* Escalate to expert */ break;
    default:         /* Safe to send */ break;
}
```

### cURL

```bash
curl -X POST https://app.bookbag.ai/api/v1/gate/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: bk_gate_xxx" \
  -d '{
    "input": "What is my refund policy?",
    "output": "You can get a full refund within 90 days, no questions asked.",
    "context": { "channel": "support_chat" },
    "metadata": { "session_id": "s_abc123" }
  }'
```

---

## How the Gate Works

When you call `gate.evaluate()`, Bookbag runs your AI output through a multi-stage evaluation pipeline:

```
1. Your app sends (input, output) to the Gate API
                    │
2. Bookbag loads your project's taxonomy template
   (defines WHAT to evaluate: hallucination, tone, compliance, etc.)
                    │
3. The configured LLM evaluates the output against every rubric
   in your taxonomy and produces scores + a verdict
                    │
4. Policy rules translate the verdict into an action
   (allow / review / block / require_sme)
                    │
5. Response returned to your app with:
   - decision (what Bookbag thinks)
   - policy_action (what your app should do)
   - flags (what triggered)
   - confidence, scores, rationale (why)
   - audit_id (for compliance trail)
                    │
6. Audit trail persisted — every evaluation is logged,
   searchable, and exportable from the admin dashboard
```

The entire flow happens synchronously. Typical latency is **1–4 seconds** depending on model and evaluation depth.

---

## API Reference

### Client

**Python:**
```python
from bookbag import BookbagClient

client = BookbagClient(
    api_key="bk_gate_xxx",              # Required — your Gate API key
    base_url="https://app.bookbag.ai"   # Optional — defaults to production
)
```

**Node.js:**
```javascript
const { BookbagClient } = require('@bookbag/sdk');

const client = new BookbagClient({
    apiKey: 'bk_gate_xxx',               // Required — your Gate API key
    baseUrl: 'https://app.bookbag.ai'    // Optional — defaults to production
});
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `api_key` / `apiKey` | Yes | — | Gate API key from your project settings. Starts with `bk_gate_`. |
| `base_url` / `baseUrl` | No | `https://app.bookbag.ai` | Bookbag server URL. Override for self-hosted or local development. |

### gate.evaluate()

Sends an AI output for evaluation. Returns the decision synchronously.

**Python:**
```python
result = client.gate.evaluate(
    input="Customer's message or prompt",
    output="The AI-generated response to evaluate",
    context={"channel": "support_chat", "locale": "en-US"},    # Optional
    metadata={"session_id": "abc", "model": "gpt-4o-mini"}     # Optional
)
```

**Node.js:**
```javascript
const result = await client.gate.evaluate({
    input: "Customer's message or prompt",
    output: 'The AI-generated response to evaluate',
    context: { channel: 'support_chat', locale: 'en-US' },     // Optional
    metadata: { session_id: 'abc', model: 'gpt-4o-mini' }      // Optional
});
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | Yes | The user's input, prompt, or question that triggered the AI response. Provides context for evaluation. |
| `output` | string | Yes | The AI-generated response to evaluate. This is what Bookbag scores. |
| `context` | object | No | Contextual information about where this interaction is happening. Use for routing rules and analytics. Common fields: `channel`, `locale`, `decision_type`, `department`. |
| `metadata` | object | No | Arbitrary metadata attached to the evaluation record. Useful for tracing and debugging. Common fields: `session_id`, `model`, `user_id`, `endpoint`, `request_id`. |

### Response Object

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
  "scores": {
    "correctness": 3,
    "tone": 5,
    "safety": 5,
    "completeness": 4
  },
  "rationale": "The stated refund timeframe (90 days) is not supported by the company's policy documents, which specify 30 days. This constitutes a factual hallucination.",
  "evaluation_ms": 2340
}
```

---

## Response Fields — Deep Dive

### `decision`

**Type:** `string` — `"allow"` | `"flag"` | `"block"` | `"queued"`

What Bookbag's AI evaluation concluded about the output quality.

| Value | Meaning | When it happens |
|-------|---------|-----------------|
| `allow` | Output passed all checks. Safe to send. | AI verdict is `safe_to_deploy` with high confidence. |
| `flag` | Output has potential issues but isn't critically wrong. | AI found minor issues (tone, completeness) or has medium confidence. |
| `block` | Output has critical problems. Should not be sent. | AI verdict is `blocked` — hallucination, policy violation, safety issue. |
| `queued` | No AI evaluation performed. Task queued for human review. | Project uses `human` review mode — no AI decision is made. |

**How to use it:** `decision` is what the AI *thinks*. `policy_action` is what your app *should do*. In most cases, act on `policy_action` rather than `decision` directly, because policy rules may override the raw AI decision (e.g., auto-approving low-risk flags, or blocking medium-confidence results in high-stakes domains).

---

### `risk`

**Type:** `string | null` — `"low"` | `"medium"` | `"high"`

Aggregated risk level derived from the evaluation. `null` when the project uses human-only review mode.

| Value | Meaning |
|-------|---------|
| `low` | No issues detected. Confidence is high. |
| `medium` | Minor issues or moderate confidence. May warrant review. |
| `high` | Critical issues found. Hallucination, policy violation, or safety concern. |

**How to use it:** Risk level is useful for dashboards, alerting, and SLA prioritization. High-risk evaluations should trigger your most urgent review workflow.

---

### `flags`

**Type:** `string[]`

List of failure categories triggered during evaluation. Each flag corresponds to a rubric dimension in your taxonomy template where the AI response scored poorly.

Common flags (depend on your taxonomy template):

| Flag | Description |
|------|-------------|
| `hallucination` | Response contains information not supported by context or facts |
| `policy_violation` | Response violates company policy or guidelines |
| `tone_issue` | Response tone doesn't match brand voice or is inappropriate |
| `incomplete_response` | Response doesn't fully address the user's question |
| `safety` | Response contains potentially harmful content |
| `compliance` | Response violates regulatory or legal requirements |
| `factual_error` | Response contains verifiably incorrect information |

**How to use it:** Flags tell you *what* went wrong. Use them for routing (e.g., send `hallucination` flags to fact-checkers, `compliance` flags to legal), for analytics (track which categories fail most), and for user-facing error messages.

```python
if "hallucination" in result.flags:
    log_warning("AI hallucinated — verify facts before sending")
if "compliance" in result.flags:
    escalate_to_legal(result)
```

---

### `policy_action`

**Type:** `string` — `"allow"` | `"review"` | `"block"` | `"require_sme"` | `"queued"`

**This is the primary field your application should act on.** It's the final instruction from Bookbag after applying your project's policy rules on top of the AI evaluation.

| Value | What your app should do |
|-------|------------------------|
| `allow` | Safe to send. No action needed. |
| `review` | Send the response, but flag it for human review in your queue. The issue is non-critical. |
| `block` | **Do not send.** The response has critical issues. Show a fallback message or escalate. |
| `require_sme` | Escalate to a subject matter expert before proceeding. Used for domain-specific issues (medical, legal, financial). |
| `queued` | Human-only project. Task created and queued for reviewer. No AI decision was made. |

**`decision` vs `policy_action`:** The AI might say `flag` (medium concern), but your policy might escalate that to `block` if the flag category is `compliance`. Or the AI might say `flag`, but your policy auto-approves it because the confidence is above your threshold. Always act on `policy_action`.

---

### `enforced`

**Type:** `boolean`

Whether your project runs in **enforced** or **advisory** mode.

| Mode | `enforced` | Meaning |
|------|-----------|---------|
| Advisory | `false` | Bookbag provides recommendations. Your app decides what to do. You can ignore `policy_action`. |
| Enforced | `true` | `policy_action` is a directive. Your app should obey it. Violations are logged. |

**How to use it:** In early rollout, use advisory mode to monitor what Bookbag would do without impacting production. Switch to enforced mode once you trust the taxonomy and policy configuration.

---

### `audit_id`

**Type:** `string`

Unique identifier for this evaluation in Bookbag's audit trail. Format: `gate_eval_{task_id}_{annotation_id}`.

**How to use it:** Log this alongside your application's request ID for end-to-end traceability. Use it to:
- Look up the full evaluation in the Bookbag admin dashboard
- Reference in compliance reports
- Correlate with customer complaints ("What did QA say about this response?")

```python
logger.info(f"AI response evaluated", extra={
    "audit_id": result.audit_id,
    "decision": result.decision,
    "request_id": request.id
})
```

---

### `task_id`

**Type:** `integer`

The ID of the task created in Bookbag for this evaluation. Visible in the project's Tasks tab in the admin dashboard.

**How to use it:** Use for deep-linking into the Bookbag admin to inspect the full evaluation, view the annotation, see pipeline stages, or trigger a re-evaluation.

---

### `confidence`

**Type:** `float | null` — Range: `0.0` to `1.0`

How confident the AI evaluator is in its assessment. `null` when using human-only review mode.

| Range | Interpretation |
|-------|---------------|
| `0.9 – 1.0` | Very confident. The evaluation is highly reliable. |
| `0.7 – 0.9` | Confident. Standard reliability. |
| `0.5 – 0.7` | Uncertain. Consider routing to a human reviewer. |
| `< 0.5` | Low confidence. The AI isn't sure — human review recommended. |

**How to use it:** Confidence is a key input for routing decisions. Many teams configure policy rules like: "If confidence < 0.7 and the decision is `allow`, route to human review anyway."

```python
if result.decision == "allow" and result.confidence < 0.7:
    # AI says it's fine but isn't sure — get a human to verify
    queue_for_review(result)
```

---

### `scores`

**Type:** `object`

Rubric scores from your taxonomy template. Each key is a dimension defined in your template, and the value is a numeric score (typically 1–5).

Example for a customer support taxonomy:
```json
{
  "correctness": 3,
  "tone": 5,
  "safety": 5,
  "completeness": 4,
  "policy_adherence": 2
}
```

**How to use it:** Scores provide granular insight beyond the binary decision. Use them for:
- **Analytics:** Track average scores per dimension over time to identify systematic weaknesses
- **Targeted routing:** Route low-correctness results to fact-checkers, low-tone results to brand reviewers
- **Model comparison:** Compare scores across different AI models to find the best performer per dimension
- **Training data:** Export low-scoring responses as training examples for fine-tuning

---

### `rationale`

**Type:** `string`

The AI evaluator's explanation of why it made this decision. Written in plain language.

Example:
> "The stated refund timeframe (90 days) is not supported by the company's policy documents, which specify 30 days. This constitutes a factual hallucination. The tone and completeness of the response are otherwise acceptable."

**How to use it:** Surface the rationale to human reviewers so they have context. Include it in escalation tickets. Use it to audit whether the evaluator's reasoning is sound.

---

### `evaluation_ms`

**Type:** `integer`

Wall-clock time for the evaluation in milliseconds. Includes model inference, taxonomy scoring, and policy evaluation.

| Range | Meaning |
|-------|---------|
| `500 – 1500ms` | Fast. Single-pass evaluation with a small model. |
| `1500 – 4000ms` | Standard. Single or two-pass evaluation. |
| `4000 – 10000ms` | Deep. Multi-pass pipeline with expert review stage. |

**How to use it:** Monitor this for SLA compliance. If latency matters, use a faster model for Stage 1 and single-pass evaluation depth.

---

## Review Modes

Configure review mode when creating a project. It controls how evaluations are processed.

### `automated` — Full AI, Real-Time

```
Input/Output → AI evaluates → Decision returned immediately
```

- AI runs the full evaluation pipeline (1, 2, or 3 passes depending on evaluation depth)
- Decision is returned synchronously in the API response
- No human involvement — the AI's decision is final
- Results appear in the admin dashboard for monitoring

**Best for:** High-volume, low-risk use cases. Chatbots, content generation, internal tools.

### `human` — Human-Only, Queued

```
Input/Output → Task created → Queued for human reviewer → decision: "queued"
```

- No AI evaluation is performed
- A task is created in Bookbag and assigned to the project's human review queue
- The API returns immediately with `decision: "queued"` and `policy_action: "queued"`
- Human reviewers evaluate using the same taxonomy template in the Bookbag dashboard
- Use webhooks or polling to get the human decision later

**Best for:** High-stakes decisions (medical, legal, financial), gold-standard data collection, model evaluation benchmarks.

### `assisted` — AI + Human, Hybrid

```
Input/Output → AI evaluates → Decision returned immediately
                                 └→ Human review queued async (for training data)
```

- AI runs the full evaluation pipeline and returns a decision synchronously — same as `automated`
- Additionally, tasks matching your escalation rules are queued for human review in the background
- The human review is asynchronous — it doesn't block the API response
- Human annotations become training data for improving the AI evaluator over time

**Best for:** Production systems where you want real-time decisions AND continuous human oversight. The AI handles the critical path, humans generate training signal.

**Escalation rules** (configured per project) control which tasks get human review:
- **Flagged issues only:** Only `needs_fix` or `blocked` verdicts
- **Low confidence:** Anything below your confidence threshold
- **Random sample:** Random % of all evaluations for spot-checking
- **All items:** Every evaluation gets human review (most thorough)
- **Custom rules:** Combine multiple criteria

---

## Evaluation Depth

Controls how many AI passes run per evaluation. More passes improve accuracy but increase latency and cost.

### Single Pass (`fast`)

```
Stage 1: Annotation → Final Decision
```

One LLM call. The AI evaluates the output against your taxonomy and returns a verdict. Fastest and cheapest.

- **Latency:** 500–2000ms
- **Cost:** 1x model cost (Stage 1 model's `credit_cost_per_call`)
- **Best for:** High-volume, low-stakes evaluations

### Two Pass (`standard`)

```
Stage 1: Annotation → Stage 2: QA Verification → Final Decision
```

Two LLM calls. Stage 1 produces an initial evaluation. Stage 2 reviews Stage 1's work — checking for errors, verifying the verdict, and potentially overriding it.

Stage 2 only triggers when escalation rules match (non-safe verdict, low confidence, flagged category). Not every evaluation gets two passes.

- **Latency:** 1500–4000ms (when Stage 2 triggers)
- **Cost:** 1–2x model cost (Stage 1 + Stage 2 model costs, when triggered)
- **Best for:** Production systems where accuracy matters more than speed

### Three Pass (`deep`)

```
Stage 1: Annotation → Stage 2: QA Verification → Stage 3: Expert Review → Final Decision
```

Three LLM calls. Stage 3 is a deep expert review that fires on disagreements between Stage 1 and Stage 2, high-severity findings, or policy/compliance categories.

- **Latency:** 3000–10000ms (when all stages trigger)
- **Cost:** 1–3x model cost
- **Best for:** Compliance-critical, high-stakes evaluations (medical, legal, financial)

### Per-Stage Model Selection

Each stage can use a different model. Common pattern:

| Stage | Model | Reasoning |
|-------|-------|-----------|
| Stage 1 | `gpt-4o-mini` | Fast, cheap — handles the bulk of evaluations |
| Stage 2 | `gpt-4o` | Smarter — catches what Stage 1 missed |
| Stage 3 | `o3` | Best available — for the hardest cases |

Configure per-stage models when creating or editing a project. Each model has its own `credit_cost_per_call`, so you can optimize cost vs quality.

---

## Policy System

Policies translate AI evaluation results into actionable instructions for your application. Configure them in the **Policy** tab of your project.

### How Policy Works

```
AI produces evaluation (verdict, confidence, flags, scores)
    → Policy rules evaluate the result
    → Policy produces: policy_action + enforced flag
    → Returned to your app
```

### Policy Actions

| Action | Trigger | Your app should... |
|--------|---------|-------------------|
| `allow` | Verdict is `safe_to_deploy`, confidence above threshold | Send the response normally |
| `review` | Minor issues detected, medium confidence | Send but queue for async human review |
| `block` | Critical issues (`blocked` verdict, safety flags) | Do not send. Show fallback or escalate. |
| `require_sme` | Domain-specific concerns (compliance, legal, medical) | Route to subject matter expert before proceeding |

### Policy Configuration Options

| Setting | Description |
|---------|-------------|
| **Routing rules** | Map verdicts to actions: `safe_to_deploy` → `allow`, `needs_fix` → `review`, `blocked` → `block` |
| **Risk escalation** | Override routing based on risk level: `high` risk always → `block` regardless of verdict |
| **Flag-based rules** | Escalate specific categories: `compliance` flags always → `require_sme` |
| **Confidence threshold** | Auto-approve above threshold, escalate below: confidence > 0.9 → `allow`, < 0.6 → `review` |
| **Auto-approval** | High-confidence + low-risk results skip review entirely |
| **Enforcement mode** | Advisory (suggestions only) vs Enforced (your app must obey) |

---

## Error Handling

The SDK raises typed exceptions for common failure modes.

### Python

```python
from bookbag import BookbagClient
from bookbag.exceptions import (
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
    BookbagError
)

client = BookbagClient(api_key="bk_gate_xxx")

try:
    result = client.gate.evaluate(
        input="Customer question",
        output="AI response to evaluate"
    )
except AuthenticationError:
    # Invalid or expired API key
    # Fix: Check your API key in project settings > Gate API tab
    log.error("Invalid Bookbag API key")

except RateLimitError as e:
    # Too many requests
    # Fix: Wait and retry, or increase rate limit in key settings
    log.warning(f"Rate limited — retry after {e.reset_time}")
    time.sleep(1)
    # retry...

except InsufficientCreditsError:
    # Account has no remaining credits
    # Fix: Top up credits in billing settings
    log.error("Out of Bookbag credits — evaluation skipped")
    send_response_without_gate(output)  # Fail open

except BookbagError as e:
    # Any other Bookbag API error
    log.error(f"Bookbag error: {e} (HTTP {e.status_code})")
    send_response_without_gate(output)  # Fail open
```

### Node.js

```javascript
const { BookbagClient } = require('@bookbag/sdk');
const {
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
    BookbagError
} = require('@bookbag/sdk/errors');

const client = new BookbagClient({ apiKey: 'bk_gate_xxx' });

try {
    const result = await client.gate.evaluate({
        input: 'Customer question',
        output: 'AI response to evaluate'
    });
} catch (error) {
    if (error instanceof AuthenticationError) {
        console.error('Invalid Bookbag API key');
    } else if (error instanceof RateLimitError) {
        console.warn(`Rate limited — retry after ${error.resetTime}`);
    } else if (error instanceof InsufficientCreditsError) {
        console.error('Out of credits');
    } else if (error instanceof BookbagError) {
        console.error(`Bookbag error: ${error.message} (${error.statusCode})`);
    }

    // Fail open — send response without gating
    sendResponseWithoutGate(output);
}
```

### Error Reference

| Exception | HTTP Status | Cause | Fix |
|-----------|-------------|-------|-----|
| `AuthenticationError` | 401 | Invalid, expired, or missing API key | Regenerate key in project settings |
| `RateLimitError` | 429 | Too many requests in the rate window | Wait for `reset_time`, or increase limit in key settings |
| `InsufficientCreditsError` | 402 | Account has no remaining credits | Top up credits in billing |
| `BookbagError` | Various | Server error, network issue, invalid request | Check error message and status code |

### Fail-Open vs Fail-Closed

Choose a failure strategy for when the Gate API is unavailable:

| Strategy | Behavior | Best for |
|----------|----------|----------|
| **Fail open** | If Gate is down, send the response anyway | Customer-facing chatbots, support systems (availability > safety) |
| **Fail closed** | If Gate is down, block the response | Medical, legal, financial systems (safety > availability) |

```python
# Fail open (recommended for most apps)
try:
    result = client.gate.evaluate(input=q, output=response)
    if result.policy_action == "block":
        return fallback()
    return response
except BookbagError:
    return response  # Gate is down — send anyway

# Fail closed (for high-stakes domains)
try:
    result = client.gate.evaluate(input=q, output=response)
    if result.policy_action == "block":
        return fallback()
    return response
except BookbagError:
    return fallback()  # Gate is down — don't risk it
```

---

## Integration Patterns

### Basic Gating

The simplest pattern — evaluate before sending.

```python
def handle_chat(user_message):
    ai_response = my_llm.generate(user_message)

    result = bookbag.gate.evaluate(
        input=user_message,
        output=ai_response
    )

    if result.policy_action in ("block", "require_sme"):
        return "I'm unable to help with that. Let me connect you with a specialist."

    return ai_response
```

### Express Middleware

Gate every AI response automatically in Express.

```javascript
const { BookbagClient } = require('@bookbag/sdk');

const bookbag = new BookbagClient({
    apiKey: process.env.BOOKBAG_API_KEY
});

function bookbagGate() {
    return async (req, res, next) => {
        if (!res.aiResponse) return next();

        try {
            const result = await bookbag.gate.evaluate({
                input: req.body?.message || '',
                output: res.aiResponse,
                context: { channel: 'api' },
                metadata: { session_id: req.sessionID, endpoint: req.path }
            });

            res.gateResult = result;

            if (result.policy_action === 'block') {
                return res.status(403).json({
                    error: 'Response blocked by quality policy',
                    audit_id: result.audit_id,
                    flags: result.flags
                });
            }

            next();
        } catch (error) {
            console.error('[Bookbag] Gate error:', error.message);
            next(); // Fail open
        }
    };
}

// Usage
app.post('/api/chat', generateAiResponse, bookbagGate(), sendResponse);
```

### FastAPI Middleware

```python
from bookbag import BookbagClient
from bookbag.exceptions import BookbagError

bookbag = BookbagClient(api_key=os.environ["BOOKBAG_API_KEY"])

@app.post("/api/chat")
async def chat(request: ChatRequest):
    ai_response = await generate_response(request.message)

    try:
        result = bookbag.gate.evaluate(
            input=request.message,
            output=ai_response,
            context={"channel": "api"},
            metadata={"user_id": request.user_id}
        )

        if result.policy_action == "block":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Response blocked by quality policy",
                    "audit_id": result.audit_id,
                    "flags": result.flags
                }
            )

        return {
            "response": ai_response,
            "quality": {
                "decision": result.decision,
                "confidence": result.confidence,
                "audit_id": result.audit_id
            }
        }
    except BookbagError:
        return {"response": ai_response}  # Fail open
```

### Async Processing

For high-throughput systems, evaluate in the background and handle results asynchronously.

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

async def evaluate_async(input_text, output_text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: bookbag.gate.evaluate(input=input_text, output=output_text)
    )

# Fire-and-forget pattern (send immediately, evaluate async)
async def handle_message(user_msg):
    response = await generate_response(user_msg)
    send_response(response)  # Send immediately

    # Evaluate in background
    result = await evaluate_async(user_msg, response)
    if result.policy_action == "block":
        retract_response(response)  # Pull it back if blocked
        notify_user("Our quality system flagged an issue. A corrected response is on the way.")
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                        │
│                                                             │
│  User Input → AI Model → AI Response                        │
│                              │                              │
│                    ┌─────────▼──────────┐                   │
│                    │  Bookbag SDK       │                   │
│                    │  gate.evaluate()   │                   │
│                    └─────────┬──────────┘                   │
└──────────────────────────────┼──────────────────────────────┘
                               │ HTTPS + X-API-Key
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Bookbag Platform                          │
│                                                             │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐    │
│  │ Gate API │──▶│ AI Evaluator │──▶│ Policy Engine    │    │
│  │          │   │              │   │                  │    │
│  │ Auth     │   │ Stage 1      │   │ Verdict → Action │    │
│  │ Rate     │   │ Stage 2      │   │ Risk mapping     │    │
│  │ Limit    │   │ Stage 3      │   │ Flag rules       │    │
│  └──────────┘   └──────────────┘   └──────────────────┘    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Audit Trail — every evaluation persisted, searchable │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Admin Dashboard — review tasks, analytics, exports   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Credits and Billing

Each Gate evaluation consumes credits based on the models used and the evaluation depth.

| Depth | Models Called | Credit Cost |
|-------|-------------|-------------|
| Single pass | Stage 1 only | Stage 1 model's `credit_cost_per_call` |
| Two pass | Stage 1 + Stage 2 (when triggered) | Sum of both models' costs |
| Three pass | Stage 1 + Stage 2 + Stage 3 (when triggered) | Sum of all three models' costs |

Credit costs are set per model in the admin dashboard (Models > My Models > Edit). Common examples:

| Model | Typical Cost |
|-------|-------------|
| `gpt-4o-mini` | 0.10 credits/call |
| `gpt-4o` | 0.25 credits/call |
| `gpt-5` | 1.00 credits/call |

Stage 2 and Stage 3 only trigger when escalation rules match, so most evaluations only consume Stage 1 cost.

Monitor credit usage in the admin dashboard under Billing.
