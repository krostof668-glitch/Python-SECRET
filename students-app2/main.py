from fastapi import FastAPI
from routers import students
from db import create_db_and_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Most éled a szerver!")
    create_db_and_tables()
    print("Már fut a szerver!")
    yield
    print("A szerver leáll!")

app = FastAPI(lifespan=lifespan)
app.include_router(students.router)

@app.get("/")
async def read_root():
    return {"Message": "Hello!"}

