from fastapi import FastAPI, APIRouter
from routers import users
from contextlib import asynccontextmanager
from db import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(users.router)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/")
async def get_root():
    return {"message": "fut a szerver"}