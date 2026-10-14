from fastapi import FastAPI
from routers import books

app = FastAPI()
app.include_router(books.router)

@app.get("/")
async def root():
    return {"Message": "Weboldal"}