from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class GateResult:
    """Result from a gate evaluation."""
    decision: str           # "allow" | "flag" | "block" | "queued"
    risk: Optional[str]     # "low" | "medium" | "high"
    flags: List[str]        # Triggered failure categories
    policy_action: str      # "allow" | "review" | "block" | "require_sme" | "queued"
    enforced: bool          # Whether this is enforced or advisory
    audit_id: str           # Unique audit trail ID
    task_id: int            # Task ID in Bookbag
    confidence: Optional[float] = None
    scores: Dict = field(default_factory=dict)
    rationale: str = ""
    evaluation_ms: int = 0


class GateClient:
    """
    Gate API client for real-time AI output evaluation.

    Usage:
        result = client.gate.evaluate(
            input="Customer question",
            output="AI response to evaluate"
        )

        if result.policy_action == "block":
            prevent_send()
        elif result.policy_action == "review":
            queue_for_review(result)
        else:
            send_response()
    """

    def __init__(self, client):
        self._client = client

    def evaluate(
        self,
        input: str,
        output: str,
        context: dict = None,
        metadata: dict = None,
    ) -> GateResult:
        """
        Evaluate an AI output through the decision gate.

        Args:
            input: The input/prompt that produced the AI output
            output: The AI-generated output to evaluate
            context: Optional context (channel, locale, decision_type, etc.)
            metadata: Optional metadata (session_id, model, etc.)

        Returns:
            GateResult with decision, risk, flags, and policy_action
        """
        response = self._client._request("POST", "/api/v1/gate/evaluate", {
            "input": input,
            "output": output,
            "context": context or {},
            "metadata": metadata or {},
        })

        return GateResult(
            decision=response.get("decision", "flag"),
            risk=response.get("risk"),
            flags=response.get("flags", []),
            policy_action=response.get("policy_action", "review"),
            enforced=response.get("enforced", False),
            audit_id=response.get("audit_id", ""),
            task_id=response.get("task_id", 0),
            confidence=response.get("confidence"),
            scores=response.get("scores", {}),
            rationale=response.get("rationale", ""),
            evaluation_ms=response.get("evaluation_ms", 0),
        )
