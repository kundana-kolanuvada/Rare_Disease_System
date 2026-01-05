from fastapi import FastAPI

app = FastAPI(title = "AtlasDx")
@app.get("/")
def check():
    return {"status": "backend running"}