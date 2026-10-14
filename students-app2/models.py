from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class Students(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    age: int | None = None
    password: str

class StudentCreate(BaseModel):
    name: str
    email: str
    age: int | None = None
    password: str = Field(min_length=6)

class PublicStudent(BaseModel):
    id: int
    name: str
    email: str
    age: int