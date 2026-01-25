from fastapi import APIRouter, Depends, HTTPException
import logging
from pydantic import BaseModel
import sqlalchemy
from src.db import users, notes
from src.auth import pass_hash, auth_header
from datetime import UTC, datetime


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users")




# TODO set rules for values of page and page size
@router.get(
    "",
    dependencies=[Depends(auth_header.require_admin)]
)
def list_users(page: int = 1, page_size: int = 10):
    rows = users.list_users((page - 1) * page_size, page_size)
    return rows


class SignUpRequest(BaseModel):
    email: str
    password: str
@router.post(
    ""
)
def sign_up(body: SignUpRequest):
    email = body.email
    password_hash = pass_hash.hash(body.password)
    created = datetime.now(UTC)
    try:
        result = users.create_user(email, password_hash, created)
        user_id = result[0]["id"]
        logger.info(f"id added is: {user_id}")
    except sqlalchemy.exc.IntegrityError as exception:
        logger.error(exception)
        # for seeing the full trace:
        # logger.exception(exception)
        raise HTTPException(status_code=400, detail="Email already registered")
    return {
        "message": "user created successfully",
        "email": email,
        "created": created,
        "id": user_id
    }





@router.get(
    "/{user_id}",
    dependencies=[Depends(auth_header.require_owner_or_admin)]
)
def get_user(user_id: int):
    rows = users.get_user(user_id)
    if len(rows) == 0: raise HTTPException(400, f"user {user_id} does not exist")
    return rows[0]

@router.delete(
    "/{user_id}",
    dependencies=[Depends(auth_header.require_admin)]
)
def delete_user(user_id: int):
    notes_deleted = users.delete_user_notes(user_id)
    users_deleted = users.delete_user(user_id)
    if len(users_deleted) == 0: raise HTTPException(400, f"user {user_id} does not exist")
    logger.info(f"deleted user {user_id} and {len(notes_deleted)} notes")
    return { "message": f"user {user_id} was deleted successfully, along with {len(notes_deleted)} notes" }





@router.get(
    "/{user_id}/notes", 
    dependencies=[Depends(auth_header.require_owner_or_admin)]
)
def get_notes(user_id: int):
    rows = notes.list_notes(user_id)
    return rows

class AddNoteRequest(BaseModel):
    name: str
    note: str
@router.post(
    "/{user_id}/notes", 
    dependencies=[Depends(auth_header.require_owner_or_admin)]
)
def add_note(user_id: int, body: AddNoteRequest):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.create_note(user_id, body.name, body.note, datetime.now(UTC))
    if len(rows) == 0: raise HTTPException(400, f"could not add note for user {user_id}")
    return {
        "message": "note added successfully",
        "details": rows[0]
    }





@router.get(
    "/{user_id}/notes/{note_id}", 
    dependencies=[Depends(auth_header.require_owner_or_admin)]
)
def get_note(user_id: int, note_id: int):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.get_note(user_id, note_id)
    if len(rows) == 0: raise HTTPException(400, f"note {note_id} for user {user_id} does not exist")
    return rows[0]

@router.delete(
    "/{user_id}/notes/{note_id}", 
    dependencies=[Depends(auth_header.require_owner_or_admin)]
)
def remove_note(user_id: int, note_id: int):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.delete_note(note_id)
    if len(rows) == 0: raise HTTPException(400, f"note {note_id} for user {user_id} does not exist")
    return {"message": f"note {note_id} for user {user_id} was deleted successfully"}

class UpdateNoteRequest(BaseModel):
    note: str
@router.put(
    "/{user_id}/notes/{note_id}", 
    dependencies=[Depends(auth_header.require_owner_or_admin)]
)
def update_note(user_id: int, note_id: int, body: UpdateNoteRequest):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.update_note(note_id, body.note)
    if len(rows) == 0: raise HTTPException(400, f"note {note_id} for user {user_id} does not exist")
    logger.info(f"note {note_id} of user {user_id} was updated")
    return {"message": f"note {note_id} for user {user_id} was updated successfully"}
