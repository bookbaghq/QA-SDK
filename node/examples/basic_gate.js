/**
 * Basic Gate API example — evaluate an AI output before sending it.
 */
const { BookbagClient } = require('../src');

async function main() {
    const client = new BookbagClient({
        apiKey: 'bk_gate_YOUR_KEY_HERE',
        baseUrl: 'http://localhost:3000'
    });

    const result = await client.gate.evaluate({
        input: 'What is my account balance?',
        output: 'Your balance is $5,230.00 as of today.',
        context: { channel: 'support_chat' },
        metadata: { session_id: 'abc123', model: 'gpt-4o-mini' }
    });

    console.log(`Decision: ${result.decision}`);
    console.log(`Risk: ${result.risk}`);
    console.log(`Policy Action: ${result.policy_action}`);
    console.log(`Flags: ${result.flags.join(', ') || 'none'}`);
    console.log(`Confidence: ${result.confidence}`);
    console.log(`Audit ID: ${result.audit_id}`);
    console.log(`Evaluation Time: ${result.evaluation_ms}ms`);

    if (result.policy_action === 'block') {
        console.log('BLOCKED — do not send this response');
    } else if (result.policy_action === 'review') {
        console.log('FLAGGED — queue for human review');
    } else {
        console.log('ALLOWED — safe to send');
    }
}

main().catch(console.error);
