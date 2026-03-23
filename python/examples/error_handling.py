"""
Error handling example — gracefully handle API errors.
"""
from bookbag import BookbagClient
from bookbag.exceptions import AuthenticationError, RateLimitError, InsufficientCreditsError, BookbagError

client = BookbagClient(api_key="bk_gate_YOUR_KEY_HERE", base_url="http://localhost:3000")

try:
    result = client.gate.evaluate(
        input="Customer question",
        output="AI response to check"
    )
    print(f"Decision: {result.decision}, Action: {result.policy_action}")

except AuthenticationError:
    print("Invalid API key — check your credentials")

except RateLimitError as e:
    print(f"Rate limited — retry after {e.reset_time}")

except InsufficientCreditsError:
    print("Out of credits — top up your account")

except BookbagError as e:
    print(f"Bookbag error: {e} (status {e.status_code})")
