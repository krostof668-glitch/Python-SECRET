from pydantic import BaseModel
from sqlmodel import SQLModel, Field
import datetime

class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    birthDate: datetime.date
    password: str
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class usersCreate(BaseModel):
    name: str
    email: str = Field(unique=True)
    birthDate: datetime.date
    password: str
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class UsersPublic(BaseModel):
    id: int
    name: str
    email: str
    birthDate: datetime.date
    created_at: datetime.datetime