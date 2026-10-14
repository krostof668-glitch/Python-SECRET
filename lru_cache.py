# lru_cache.py
from fastapi import FastAPI
from functools import lru_cache

app = FastAPI()

@lru_cache(maxsize=128)
def compute_expensive(x: int):
    return x * x * x

@app.get("/compute/{x}")
def compute(x: int):
    return {"result": compute_expensive(x)}