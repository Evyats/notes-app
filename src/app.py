from contextlib import asynccontextmanager
from email.policy import HTTP
from sqlite3 import IntegrityError
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from jose import ExpiredSignatureError
import psycopg2
from pydantic import BaseModel
import sqlalchemy
from .auth import jwt, pass_hash
from . import config, db
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





class SignInRequest(BaseModel):
    email: str
    password: str
@app.post("/auth/login")
def sign_in(body: SignInRequest):

    rows = db.execute_sql(
        """
        SELECT id, password_hash
        FROM users
        WHERE email=:email
        """,
        {"email": body.email}
    )
    
    if len(rows) < 1:
        logger.info("email is not registered")
        raise HTTPException(400, "Invalid credentials")

    if not pass_hash.verify(body.password, rows[0]["password_hash"]):
        logger.info("incorrect password")
        raise HTTPException(400, "Invalid credentials")

    user_id = rows[0]["id"]
    token = jwt.create_access_token(user_id, 30, 0)
    
    return {
        "user_id": user_id,
        "access_token": token,
        "token_type": "bearer"
    }




@app.get("/auth/me")
def me(authorization: str = Header(...)):
    try:
        user_id = _verify_auth_header(authorization)
    except ExpiredSignatureError:
        logger.info("token is expired")
        raise HTTPException(400, "token is invalid")
    except Exception as exception:
        logger.info(f"authorization is invalid: {exception}")
        raise HTTPException(400, "token is invalid")
    return {
        "message": f"your user id is: {user_id} and your token is valid"
    }


def _verify_auth_header(auth_header):
    if not auth_header: raise Exception("Missing Authorization header")
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token: raise Exception("Invalid Authorization header")
    user_id = jwt.decode_access_token(token)
    return user_id




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





# TODO add authorization for admin only
# TODO set rules for values of paage and page size
@app.get("/api/users")
def list_users(page:int = 1, page_size:int = 10):
    rows = db.execute_sql(
        """
        SELECT id, email, created
        FROM users
        ORDER BY created DESC
        OFFSET :offset
        LIMIT :limit
        """,
        {"offset": (page-1)*page_size, "limit": page_size} 
    )
    return rows


# TODO allow only for authorized
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    rows = db.execute_sql(
        """
        SELECT u.id, u.email, u.created, COUNT(n.note) AS notes_count
        FROM users u
        LEFT JOIN notes n ON u.id=n.user_id
        WHERE u.id=:user_id
        GROUP BY u.id
        """,
        {"user_id": user_id}
    )
    if len(rows) == 0: raise HTTPException(400, f"user {user_id} does not exist")
    return rows[0]


# TODO allow only for authorized
@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    users_deleted = db.execute_sql(
        """
        DELETE FROM users 
        WHERE id=:user_id 
        RETURNING *
        """,
        {"user_id": user_id}
    )
    notes_deleted = db.execute_sql(
        """
        DELETE FROM notes 
        WHERE user_id=:user_id 
        RETURNING *
        """,
        {"user_id": user_id}
    )
    
    if len(users_deleted) == 0:
        raise HTTPException(400, f"user {user_id} does not exist")
    return {
        "message": f"user {user_id} was deleted successfully, along with {len(notes_deleted)} notes",
    }
