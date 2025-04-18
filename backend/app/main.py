# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import meta, data
from fastapi.responses import Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router, prefix="/meta")
app.include_router(data.router, prefix="/data")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)
