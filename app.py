from fastapi import FastAPI


app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": 200,
        "message": "healthy"
    }