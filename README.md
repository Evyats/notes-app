
# Deployed
python -m uvicorn src.app:app --host 0.0.0.0 --reload --port $PORT


# Local
### Service
python -m uvicorn src.app:app --host 0.0.0.0 --reload --port 8123
### DB
docker compose up