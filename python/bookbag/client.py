import json
import urllib.request
import urllib.error
from .gate import GateClient
from .exceptions import BookbagError, AuthenticationError, RateLimitError, InsufficientCreditsError


class BookbagClient:
    """
    Bookbag SDK client.

    Usage:
        client = BookbagClient(api_key="bk_gate_xxx")
        result = client.gate.evaluate(
            input="What is my balance?",
            output="Your balance is $5,230."
        )
    """

    def __init__(self, api_key: str, base_url: str = "https://app.bookbag.ai"):
        if not api_key:
            raise AuthenticationError("API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.gate = GateClient(self)

    def _request(self, method: str, path: str, body: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            try:
                error_data = json.loads(body_text)
            except json.JSONDecodeError:
                error_data = {"error": body_text}

            error_msg = error_data.get("error", f"HTTP {e.code}")

            if e.code == 401:
                raise AuthenticationError(error_msg, status_code=e.code, response=error_data)
            elif e.code == 429:
                raise RateLimitError(error_msg, status_code=e.code, response=error_data,
                                    reset_time=error_data.get("resetTime"))
            elif "insufficient" in error_msg.lower() or "credit" in error_msg.lower():
                raise InsufficientCreditsError(error_msg, status_code=e.code, response=error_data)
            else:
                raise BookbagError(error_msg, status_code=e.code, response=error_data)
        except urllib.error.URLError as e:
            raise BookbagError(f"Connection error: {e.reason}")
