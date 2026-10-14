from types_of_books.book_type import BookType
from fastapi import APIRouter

router = APIRouter(prefix="/books", tags=["books"])

@router.get("")
async def get_all_books() -> dict:
    return {"data": []}

@router.get("/title")
async def get_title(title: BookType):
    return title