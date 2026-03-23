"""
Basic Gate API example — evaluate an AI output before sending it.
"""
from bookbag import BookbagClient

client = BookbagClient(
    api_key="bk_gate_YOUR_KEY_HERE",
    base_url="http://localhost:3000"
)

# Evaluate an AI response before sending
result = client.gate.evaluate(
    input="What is my account balance?",
    output="Your balance is $5,230.00 as of today.",
    context={"channel": "support_chat"},
    metadata={"session_id": "abc123", "model": "gpt-4o-mini"}
)

print(f"Decision: {result.decision}")
print(f"Risk: {result.risk}")
print(f"Policy Action: {result.policy_action}")
print(f"Flags: {result.flags}")
print(f"Confidence: {result.confidence}")
print(f"Audit ID: {result.audit_id}")
print(f"Evaluation Time: {result.evaluation_ms}ms")

# Act on the policy action
if result.policy_action == "block":
    print("BLOCKED — do not send this response")
elif result.policy_action == "review":
    print("FLAGGED — queue for human review")
elif result.policy_action == "require_sme":
    print("ESCALATED — requires SME review")
else:
    print("ALLOWED — safe to send")
