from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    email: str | None = None
    password: str
    result: int