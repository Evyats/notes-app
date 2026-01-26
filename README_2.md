





Evernote - backend service
<very short explanation about this project - what it is generally about and what it includes>
< technologioes used here - dont forget to mention the jwt and password hashing>




Endpoints
<all endpoints listed with very short explanation, only if needed>







running locally:

- start the postgeres db:
docker compose up

- start the dastapi service:
python -m uvicorn src.app:app --host 0.0.0.0 --reload --port 8123






more commands for local development:

- Update dependencies once adding new / removing:
pip freeze > requirements.txt

- Run DB file - for db updates or granting admin permissions:
python -m src.db.db_engine

- getting auto generateed api:
http://localhost:8123/docs






deploying to the cloud:

- provide this command for starting the service:
python -m uvicorn src.app:app --host 0.0.0.0 --reload --port $PORT

- set environments variables:
PORT
DATABASE_URL







