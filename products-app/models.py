from sqlmodel import SQLModel, table, Field
from pydantic import BaseModel

class Products(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    stock: int = 1
    price: float
    country: str | None = None

class ProductCreate(BaseModel):
    name: str
    stock: int = 1
    price: float
    country: str | None = None

class ProductPublic(BaseModel):
    id: int
    name: str
    stock: int
    price: float