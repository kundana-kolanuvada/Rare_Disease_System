from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Rare Disease Diagnostic Assistant",
    description="MVP disease matching using HPO terms",
    version="0.1.0"
)

app.include_router(router)

@app.get("/")
def check():
    return {"status": "backend running"}