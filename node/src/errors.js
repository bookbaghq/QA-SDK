class BookbagError extends Error {
    constructor(message, statusCode, response) {
        super(message);
        this.name = 'BookbagError';
        this.statusCode = statusCode;
        this.response = response;
    }
}

class AuthenticationError extends BookbagError {
    constructor(message = 'Invalid API key', ...args) {
        super(message, ...args);
        this.name = 'AuthenticationError';
    }
}

class RateLimitError extends BookbagError {
    constructor(message = 'Rate limit exceeded', statusCode, response) {
        super(message, statusCode, response);
        this.name = 'RateLimitError';
        this.resetTime = response?.resetTime;
    }
}

class InsufficientCreditsError extends BookbagError {
    constructor(message = 'Insufficient credits', ...args) {
        super(message, ...args);
        this.name = 'InsufficientCreditsError';
    }
}

module.exports = { BookbagError, AuthenticationError, RateLimitError, InsufficientCreditsError };
