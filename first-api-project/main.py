from fastapi import FastAPI
from routers import students
from routers import subjects

app = FastAPI()
app.include_router(students.router)
app.include_router(subjects.router)

@app.get("/")
async def root():
    return {"Message": "Hello nagyvilág"}

