# oauth2_auth.py
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/profile")
def profile(token: str = Depends(oauth2)):
    return {"token_received": token}