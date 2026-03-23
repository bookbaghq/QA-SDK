class BookbagError(Exception):
    """Base exception for Bookbag SDK errors."""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class AuthenticationError(BookbagError):
    """Raised when the API key is invalid or missing."""
    pass

class RateLimitError(BookbagError):
    """Raised when the rate limit is exceeded."""
    def __init__(self, message="Rate limit exceeded", reset_time=None, **kwargs):
        super().__init__(message, **kwargs)
        self.reset_time = reset_time

class InsufficientCreditsError(BookbagError):
    """Raised when the account has insufficient credits."""
    pass
