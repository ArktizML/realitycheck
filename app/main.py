from fastapi import FastAPI
from app.api.events import router

app = FastAPI(title="RealityCheck API")

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}