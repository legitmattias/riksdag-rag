# backend/app/main.py
from fastapi import FastAPI
from app.api import meta, data

app = FastAPI()

app.include_router(meta.router, prefix="/meta")
app.include_router(data.router, prefix="/data")
