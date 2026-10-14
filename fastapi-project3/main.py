from fastapi import FastAPI
from db import create_db_and_tables, get_session
from contextlib import asynccontextmanager
from routers import user, post

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(user.router)
app.include_router(post.router)

@app.get("/")
async def root_api():
    return {"Message": "Él a szerver"}