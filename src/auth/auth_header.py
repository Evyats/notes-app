import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError
from ..db import users
from .jwt import decode_access_token


security = HTTPBearer()
logger = logging.getLogger(__name__)



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:                            user_id = decode_access_token(token)
    except ExpiredSignatureError:   raise HTTPException(401, "Token expired")
    except Exception:               raise HTTPException(401, "Invalid token")
    rows = users.get_user(user_id)
    if len(rows) == 0:              raise HTTPException(401, "User not found")
    return rows[0]


def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        logger.info(f"user {current_user['id']} tried to access admin only resource")
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user


def require_owner_or_admin(user_id, current_user = Depends(get_current_user)):
    if str(current_user["id"]) != user_id and not current_user.get("is_admin"):
        logger.info(f"user {current_user['id']} tried to access data of user {user_id}")
        logger.info(f"user is admin: {current_user.get('is_admin')}")
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user
    