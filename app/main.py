from fastapi import FastAPI

app = FastAPI(title="RealityCheck API")

@app.get("/health")
def health():
    return {"status": "ok"}