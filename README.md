# Evernote Backend Service

A FastAPI backend for a simple Evernote-style notes app. It provides user management, JWT-based auth, and CRUD endpoints for notes backed by PostgreSQL.

## Tech Stack

- FastAPI + Uvicorn
- PostgreSQL (via `psycopg2`)
- SQLAlchemy 2.0
- JWT authentication (`python-jose`)
- Password hashing (`passlib`)

## API Endpoints

### Auth

```
POST    /auth/login     Authenticate with email/password and receive a JWT access token.
GET     /auth/me        Verify token and return current user info.
```

### Users

```
GET     /api/users                              List users (admin only, paginated).
POST    /api/users                              Create a user account.
GET     /api/users/{user_id}                    Get a user by id.
DELETE  /api/users/{user_id}                    Delete a user and their notes (admin only).
GET     /api/users/{user_id}/notes              List notes for a user.
POST    /api/users/{user_id}/notes              Create a note for a user.
GET     /api/users/{user_id}/notes/{note_id}    Get a specific note.
DELETE  /api/users/{user_id}/notes/{note_id}    Delete a note.
PUT     /api/users/{user_id}/notes/{note_id}    Update a note.
```

### Notes

```
GET     /api/notes      List all notes (admin only, paginated).
```

## Running Locally

| Task | Command |
| --- | --- |
| Start PostgreSQL | `docker compose up` |
| Start the API | `python -m uvicorn src.app:app --host 0.0.0.0 --reload --port 8123` |

## Useful Local Commands

| Task | Command |
| --- | --- |
| Run DB scripts (schema updates / admin access token) | `python -m src.db.db_engine` |
| Update dependencies after changes | `pip freeze > requirements.txt` |
| Auto-generated API docs | `http://localhost:8123/docs` |

## Deploying

| Task | Value |
| --- | --- |
| Start Command | `python -m uvicorn src.app:app --host 0.0.0.0 --reload --port $PORT` |
| Environment Variables | `PORT`, `DATABASE_URL` |
