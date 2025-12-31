from fastapi import FastAPI
from app.api.events import router
from app.database import engine, Base
from app.schemas.event import Event

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RealityCheck API")

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}