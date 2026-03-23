/**
 * Express middleware example — gate AI responses before sending to users.
 */
const { BookbagClient } = require('../src');

const bookbag = new BookbagClient({
    apiKey: process.env.BOOKBAG_API_KEY,
    baseUrl: process.env.BOOKBAG_URL || 'https://app.bookbag.ai'
});

/**
 * Express middleware that evaluates AI responses through Bookbag Gate.
 * Blocks or flags responses based on policy.
 */
function bookbagGate(options = {}) {
    return async (req, res, next) => {
        // Skip if no AI response to evaluate
        if (!res.aiResponse) return next();

        try {
            const result = await bookbag.gate.evaluate({
                input: req.body?.message || req.body?.input || '',
                output: res.aiResponse,
                context: {
                    channel: options.channel || 'api',
                    decision_type: options.decisionType || 'customer_response'
                },
                metadata: {
                    session_id: req.sessionID,
                    endpoint: req.path
                }
            });

            // Attach result for downstream handlers
            res.gateResult = result;

            if (result.policy_action === 'block') {
                return res.status(403).json({
                    error: 'Response blocked by policy',
                    audit_id: result.audit_id,
                    flags: result.flags
                });
            }

            if (result.policy_action === 'review') {
                // Log for review but allow through
                console.warn(`[Bookbag] Flagged response: ${result.flags.join(', ')} (audit: ${result.audit_id})`);
            }

            next();
        } catch (error) {
            console.error('[Bookbag] Gate evaluation failed:', error.message);
            // Fail open — allow response if gate is unavailable
            next();
        }
    };
}

module.exports = bookbagGate;
