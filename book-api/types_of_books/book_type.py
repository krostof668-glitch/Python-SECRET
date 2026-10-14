from pydantic import BaseModel

class BookType(BaseModel):
    title: str
    author: str
    page = int
    available: int = 1
    price = float
    