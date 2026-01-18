from fastapi import APIRouter
from fastapi.params import Depends
from src.db import notes
from src.auth import auth_header



router = APIRouter(
    prefix="/api/notes", 
    dependencies=[Depends(auth_header.require_admin)]
)


# TODO set rules for values of page and page_size
@router.get("")
def list_all_notes(page: int = 1, page_size: int = 10):
    rows = notes.list_all_notes((page - 1) * page_size, page_size)
    return rows