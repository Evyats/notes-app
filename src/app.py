from contextlib import asynccontextmanager
from email.policy import HTTP
from sqlite3 import IntegrityError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import psycopg2
from pydantic import BaseModel
import sqlalchemy
from . import config, db
from .auth import pass_hash
from datetime import UTC, datetime



############### FAST API DEFINITION ###############

logger = None
settings = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup
    global logger, settings
    
    settings = config.getSettings()
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def middleware(request: Request, call_next):
    """logging the whole request:
    body = await request.body()
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {body.decode(errors='ignore')}")
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
        result = db.execute_sql(
            """
            INSERT INTO users
            (email, password_hash, created)
            VALUES
            (:email, :password_hash, :created)
            RETURNING id
            """, 
            {"email": email, "password_hash": password_hash, "created": created})
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