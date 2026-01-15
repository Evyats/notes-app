from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.params import Depends
from jose import ExpiredSignatureError
from pydantic import BaseModel
import sqlalchemy
from ...repositories import users, notes
from ...auth import jwt, pass_hash, auth_header
from datetime import UTC, datetime






router = APIRouter(
    prefix="/api/notes", 
    dependencies=[Depends(auth_header.require_admin)]
)



# TODO add authorization for admin only
# TODO set rules for values of page and page_size
@router.get("")
def list_all_notes(page: int = 1, page_size: int = 10):
    rows = notes.list_all_notes((page - 1) * page_size, page_size)
    return rows