from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="Rare Disease Diagnostic Assistant",
    description="MVP disease matching using HPO terms",
    version="0.1.0"
)

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def check():
    return {"status": "backend running"}