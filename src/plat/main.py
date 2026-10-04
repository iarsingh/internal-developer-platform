from fastapi import FastAPI
from plat.gate import check
app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/check")
def post_check(body: dict):
    return check(body, body.get("approved", False))
