const GateClient = require('./gate');
const { BookbagError, AuthenticationError, RateLimitError, InsufficientCreditsError } = require('./errors');

class BookbagClient {
    /**
     * Create a Bookbag client.
     *
     * @param {Object} options
     * @param {string} options.apiKey - Your Bookbag Gate API key (starts with bk_gate_)
     * @param {string} [options.baseUrl='https://app.bookbag.ai'] - Base URL
     */
    constructor({ apiKey, baseUrl = 'https://app.bookbag.ai' } = {}) {
        if (!apiKey) throw new AuthenticationError('API key is required');
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.gate = new GateClient(this);
    }

    async _request(method, path, body) {
        const url = `${this.baseUrl}${path}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey,
            },
        };
        if (body) options.body = JSON.stringify(body);

        const res = await fetch(url, options);
        const data = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));

        // Check both HTTP status and JSON body success field
        const isError = !res.ok || data.success === false;
        if (isError) {
            const msg = data.error || `HTTP ${res.status}`;
            const statusCode = data.status || res.status;
            if (statusCode === 401 || msg.toLowerCase().includes('api key')) throw new AuthenticationError(msg, statusCode, data);
            if (statusCode === 429 || msg.toLowerCase().includes('rate limit')) throw new RateLimitError(msg, statusCode, data);
            if (msg.toLowerCase().includes('credit')) throw new InsufficientCreditsError(msg, statusCode, data);
            throw new BookbagError(msg, statusCode, data);
        }

        return data;
    }
}

module.exports = BookbagClient;
