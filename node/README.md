# Bookbag Node.js SDK

Zero-dependency Node.js SDK for the Bookbag Decision Gate API. Uses native `fetch`.

## Install

```bash
npm install ./sdk/node
```

## Quick Start

```javascript
const { BookbagClient } = require('@bookbag/sdk');

const client = new BookbagClient({
    apiKey: 'bk_gate_YOUR_KEY_HERE',
    baseUrl: 'https://your-bookbag-instance.com'
});

const result = await client.gate.evaluate({
    input: 'Customer asks for refund',
    output: 'You are eligible for a full refund within 30 days.'
});

console.log(result.decision);       // "allow", "flag", or "block"
console.log(result.risk);           // "low", "medium", or "high"
console.log(result.policy_action);  // "allow", "review", "block", "require_sme"
console.log(result.flags);          // ["hallucination", ...] or []
console.log(result.audit_id);       // Unique audit trail ID

if (result.policy_action === 'block') {
    preventSend();
} else if (result.policy_action === 'review') {
    queueForReview(result);
} else {
    sendResponse();
}
```

## Error Handling

```javascript
const { BookbagClient, AuthenticationError, RateLimitError, InsufficientCreditsError } = require('@bookbag/sdk');

try {
    const result = await client.gate.evaluate({ input: '...', output: '...' });
} catch (e) {
    if (e instanceof AuthenticationError) console.log('Invalid API key');
    else if (e instanceof RateLimitError) console.log(`Rate limited — retry after ${e.resetTime}`);
    else if (e instanceof InsufficientCreditsError) console.log('Out of credits');
    else throw e;
}
```

## Express Middleware

```javascript
const bookbagGate = require('@bookbag/sdk/examples/express_middleware');

app.post('/api/chat', generateAIResponse, bookbagGate({ channel: 'chat' }), sendResponse);
```

## Requirements

- Node.js 18+ (native `fetch`)
- No external dependencies
