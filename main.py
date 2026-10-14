# main.py
from fastapi import FastAPI, Depends, HTTPException
from auth import authenticate_user, create_access_token, get_current_user
from rate_limit import rate_limiter
from cache import get_cache, set_cache
from health import router as health_router

app = FastAPI()
app.middleware("http")(rate_limiter)
app.include_router(health_router)

@app.post("/login")
def login(username: str, password: str):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(username)}

@app.get("/data")
def get_data(user: str = Depends(get_current_user)):
    cached = get_cache("data")
    if cached:
        return {"cached": True, "data": cached}

    result = {"message": "Fresh data", "user": user}
    set_cache("data", result)
    return {"cached": False, "data": result}