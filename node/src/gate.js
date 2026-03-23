class GateClient {
    constructor(client) {
        this._client = client;
    }

    /**
     * Evaluate an AI output through the decision gate.
     *
     * @param {Object} options
     * @param {string} options.input - The input/prompt that produced the AI output
     * @param {string} options.output - The AI-generated output to evaluate
     * @param {Object} [options.context] - Optional context (channel, locale, etc.)
     * @param {Object} [options.metadata] - Optional metadata (session_id, model, etc.)
     * @returns {Promise<Object>} Gate result with decision, risk, flags, policy_action
     */
    async evaluate({ input, output, context = {}, metadata = {} }) {
        const response = await this._client._request('POST', '/api/v1/gate/evaluate', {
            input, output, context, metadata
        });

        return {
            decision: response.decision,       // "allow" | "flag" | "block" | "queued"
            risk: response.risk,               // "low" | "medium" | "high"
            flags: response.flags || [],       // Triggered failure categories
            policy_action: response.policy_action, // "allow" | "review" | "block" | "require_sme"
            enforced: response.enforced || false,
            audit_id: response.audit_id,
            task_id: response.task_id,
            confidence: response.confidence,
            scores: response.scores || {},
            rationale: response.rationale || '',
            evaluation_ms: response.evaluation_ms || 0
        };
    }
}

module.exports = GateClient;
