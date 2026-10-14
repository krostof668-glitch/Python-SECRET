from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models import Products, ProductPublic, ProductCreate

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
async def getAll(session: Session = Depends(get_session)):
    query = select(Products)
    products = session.exec(query)
    return products.all()

@router.post("", status_code=201, response_model=ProductPublic)
async def create(prod: ProductCreate, session: Session = Depends(get_session)):
    db_prod = Products.model_validate(prod)
    session.add(db_prod)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=409, detail="Már van ilyen termék!")
    session.refresh(db_prod)
    return db_prod