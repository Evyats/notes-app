from datetime import UTC, datetime, timedelta
from jose import ExpiredSignatureError, jwt


SECRET_KEY = "change-me-to-a-long-random"
ALGO = "HS256"


def create_access_token(user_id: int, exp_seconds=10, exp_minutes=0) -> str:
    now = datetime.now(UTC)
    payload = {"sub": str(user_id), "exp": now + timedelta(seconds=exp_seconds, minutes=exp_minutes)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGO)
    return token

def decode_access_token(token: str) -> int:
    # expiration validated automatically. in case expired - raises ExpiredSignatureError
    # sub = subject. In JWT terminology it means "the identity this token belongs to."
    data = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    return int(data["sub"])
