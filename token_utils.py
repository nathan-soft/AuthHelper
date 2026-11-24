
import jwt
from datetime import datetime, timezone


def get_token_expiry(token: str | bytes) -> datetime | None:
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")

        if exp is None:
            return None

        return datetime.fromtimestamp(exp, tz=timezone.utc)

    except (jwt.InvalidTokenError, TypeError, ValueError, OverflowError):
        # Non-JWT tokens, including ordinary API keys, have no
        # expiry information that we can extract.
        return None


def is_token_valid(expiry: datetime | None) -> bool:
    if expiry is None:
        return False

    return datetime.now(timezone.utc) < expiry
