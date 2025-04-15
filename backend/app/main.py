# backend/app/main.py
from fastapi import FastAPI
from app.api import meta, data
from fastapi.responses import Response

app = FastAPI()

app.include_router(meta.router, prefix="/meta")
app.include_router(data.router, prefix="/data")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)
