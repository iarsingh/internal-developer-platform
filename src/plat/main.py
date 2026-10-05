from plat.ops import router as ops_router
from fastapi import FastAPI
from plat.gate import check
app = FastAPI()
app.include_router(ops_router, prefix="/v1")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/check")
def post_check(body: dict):
    return check(body, body.get("approved", False))
