from fastapi import FastAPI
from routers import products
from db import create_db_and_tables, get_session
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(products.router)

@app.get("/")
async def router_get():
    return "A szerver fut."