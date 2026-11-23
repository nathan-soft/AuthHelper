import jwt
from datetime import datetime, timezone

def get_token_expiry(token: str | bytes) -> datetime | None:
    decoded = jwt.decode(token, options={"verify_signature": False})
    exp = decoded.get("exp")

    if not exp:
        return None

    return datetime.fromtimestamp(exp, tz=timezone.utc)


def is_token_valid(expiry: datetime | None) -> bool:
    if not expiry:
        return False

    return datetime.now(timezone.utc) < expiry