from fastapi import APIRouter, HTTPException
import logging
from fastapi.params import Depends
from pydantic import BaseModel
from ..repositories import users
from ..auth import jwt, pass_hash, auth_header




logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")



class SignInRequest(BaseModel):
    email: str
    password: str
@router.post("/login")
def sign_in(body: SignInRequest):
    rows = users.get_user_by_email(body.email)
    
    if len(rows) < 1:
        logger.info("email is not registered")
        raise HTTPException(400, "Invalid credentials")

    if not pass_hash.verify(body.password, rows[0]["password_hash"]):
        logger.info("incorrect password")
        raise HTTPException(400, "Invalid credentials")

    user_id = rows[0]["id"]
    token = jwt.create_access_token(user_id, 1, 30)
    
    return {
        "user_id": user_id,
        "access_token": token,
        "token_type": "bearer"
    }



@router.get("/me")
def me(current_user=Depends(auth_header.get_current_user)):
    return {
        "message": f"your user id is: {current_user['id']} and your token is valid"
    }





