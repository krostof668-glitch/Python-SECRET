from student_types import StudentCreate
from fastapi import APIRouter

router = APIRouter(prefix="/students", tags=["students"])

'''Path-paraméter'''
@router.get("/items/{id}")
async def read_item(id: int):
    return {"id": id}

@router.get("")
async def get_students(classname: str | None = None, skip: int = 0, limit: int = 10):
    return {"classname": classname, "skip": skip, "limit": limit, "data": []}

@router.post("")
async def create_student(student: StudentCreate):
    return student