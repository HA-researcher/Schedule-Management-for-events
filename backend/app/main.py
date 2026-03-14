from fastapi import FastAPI

app = FastAPI(title="Smart Schedule API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to Smart Schedule API"}
