# api_key_auth.py
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()
VALID_KEYS = {"KEY123", "KEY456"}

@app.get("/secure")
def secure_endpoint(x_api_key: str = Header(None)):
    if x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"message": "Access granted"}