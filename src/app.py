from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from jose import ExpiredSignatureError
from pydantic import BaseModel
import sqlalchemy
from .auth import jwt, pass_hash
from . import config, db, routes
from .repositories import users, notes
from datetime import UTC, datetime



############### FAST API DEFINITION ###############

logger = None
settings = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup
    global logger, settings
    
    settings = config.getSettings()
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    try:
        db.check_connectivity()
        logger.info("DB connection OK")
    except:
        logger.exception("DB connection FAILED, shutting down")
        raise
    db.create_users_table()
    db.create_notes_table()

    logger.info("Server started successfully!")
    yield
    # Runs once on shutdown
    pass

app = FastAPI(lifespan=lifespan)
app.include_router(routes.auth.router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def middleware(request: Request, call_next):
    """
    # logging the whole request:
    body = await request.body()
    logger.debug(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Body: {body.decode(errors='ignore')}")
    """
    response = await call_next(request)
    """logger.info(
        "%s %s %s",
        request.method,
        request.url.path,
        response.status_code,
    )"""
    return response

############### FAST API DEFINITION ###############



@app.get("/health")
def health():
    logger.info(f"db url: {settings.DATABASE_URL}")
    logger.info(f"service port: {settings.PORT}")
    return {
        "status": 200,
        "message": "healthy"
    }




@app.get("/testings/insert_user_note_combination/{email}")
def run_code(email: str):
    pass
    result = db.execute_sql(
        "INSERT INTO users (email, password_hash) VALUES (:email, :password_hash) RETURNING id",
        {"email": email, "password_hash": "some_pass_hash"}
    )
    user_id = result[0]["id"]
    db.print_table(db.execute_sql("SELECT * FROM users"))
    db.execute_sql(
        "INSERT INTO notes (user_id, note) VALUES (:user_id, :note)",
        {"user_id": user_id, "note": "this is the content of some note"}
    )
    db.print_table(db.execute_sql("SELECT * FROM notes"))
    
    return "look at the logs"








class SignUpRequest(BaseModel):
    email: str
    password: str
@app.post("/api/users")
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
        # for seing the full trace:
        # logger.exception(exception)
        raise HTTPException(status_code=400, detail="Email already registered")
    return {
        "message": "user created successfully",
        "email": email,
        "created": created,
        "id": user_id
    }





# TODO add authorization for admin only
# TODO set rules for values of page and page size
@app.get("/api/users")
def list_users(page: int = 1, page_size: int = 10):
    rows = users.list_users((page - 1) * page_size, page_size)
    return rows


# TODO allow only for authorized
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    rows = users.get_user(user_id)
    if len(rows) == 0: raise HTTPException(400, f"user {user_id} does not exist")
    return rows[0]


# TODO allow only for authorized
@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    notes_deleted = users.delete_user_notes(user_id)
    users_deleted = users.delete_user(user_id)
    if len(users_deleted) == 0: raise HTTPException(400, f"user {user_id} does not exist")
    logger.info(f"deleted user {user_id} and {len(notes_deleted)} notes")
    return { "message": f"user {user_id} was deleted successfully, along with {len(notes_deleted)} notes" }



# TODO add authorization for admin only
# TODO set rules for values of page and page_size
@app.get("/api/notes")
def list_all_notes(page: int = 1, page_size: int = 10):
    rows = notes.list_all_notes((page - 1) * page_size, page_size)
    return rows


# TODO allow only for authorized
@app.get("/api/users/{user_id}/notes")
def get_notes(user_id: int):
    rows = notes.list_notes(user_id)
    return rows



# TODO allow only for authorized
class AddNoteRequest(BaseModel):
    note: str
@app.post("/api/users/{user_id}/notes")
def add_note(user_id: int, body: AddNoteRequest):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.create_note(user_id, body.note, datetime.now(UTC))
    if len(rows) == 0: raise HTTPException(400, f"could not add note for user {user_id}")
    return {
        "message": "note added successfully",
        "details": rows[0]
    }


# TODO allow only for authorized
@app.get("/api/users/{user_id}/notes/{note_id}")
def get_note(user_id: int, note_id: int):
    pass
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.get_note(user_id, note_id)
    if len(rows) == 0: raise HTTPException(400, f"note {note_id} for user {user_id} does not exist")
    return rows[0]


# TODO allow only for authorized
@app.delete("/api/users/{user_id}/notes/{note_id}")
def remove_note(user_id: int, note_id: int):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.delete_note(note_id)
    if len(rows) == 0: raise HTTPException(400, f"note {note_id} for user {user_id} does not exist")
    return {"message": f"note {note_id} for user {user_id} was deleted successfully"}


# TODO allow only for authorized
class UpdateNoteRequest(BaseModel):
    note: str
@app.put("/api/users/{user_id}/notes/{note_id}")
def update_note(user_id: int, note_id: int, body: UpdateNoteRequest):
    if not users.user_exists(user_id): raise HTTPException(400, f"user {user_id} does not exist")
    rows = notes.update_note(note_id, body.note)
    if len(rows) == 0: raise HTTPException(400, f"note {note_id} for user {user_id} does not exist")
    logger.info("note {note_id} of user {user_id} was updated")
    return {"message": f"note {note_id} for user {user_id} was updated successfully"}
