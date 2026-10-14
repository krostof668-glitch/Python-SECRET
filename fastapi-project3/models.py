from sqlmodel import Session, table, Field, SQLModel, Relationship
from datetime import datetime, date, timezone


'''Adattáblák (table=True)'''
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    password: str
    birthdate: date
    salary: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    posts: list["Post"] = Relationship(back_populates="author")

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id")

    author: User = Relationship(back_populates="posts")

'''Kimeneti modellek:'''
class UserPublic(SQLModel):
    id: int
    name: str
    email: str
    birthdate: date
    salary: int
    created_at: datetime

class PostPublic(SQLModel):
    id: int
    title: str
    content: str
    created_at: datetime
    user_id: int


'''Bemeneti modellek'''
class CreateUser(SQLModel):
    name: str
    email: str = Field(unique=True)
    password: str
    birthdate: date
    salary: int

class PostCreate(SQLModel):
    title: str
    content: str

'''Bővített kimeneti modellek:'''
class UserPublicWithPosts(UserPublic):
    posts: list[PostPublic] = []

class PostPublicWithAuthor(PostPublic):
    author: UserPublic