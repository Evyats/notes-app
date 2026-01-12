
# Deployed
python -m uvicorn src.app:app --host 0.0.0.0 --reload --port $PORT


# Local
### DB
docker compose up
### Service
python -m uvicorn src.app:app --host 0.0.0.0 --reload --port 8123
### Update dependencies
pip freeze > requirements.txt
### Auto UI
http://localhost:8123/docs