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
app.include_router(routes.api.users.router)
app.include_router(routes.api.notes.router)



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

