from fastapi import FastAPI
from app.api.events import router
from app.database import engine, Base
from app.api.auth import router as auth_router
from app.api import pages
from fastapi.staticfiles import StaticFiles



Base.metadata.create_all(bind=engine)

app = FastAPI(title="RealityCheck API")

app.include_router(router)
app.include_router(auth_router)
app.include_router(pages.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}