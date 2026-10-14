from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models import Users, UsersPublic, usersCreate
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", status_code=200, response_model=list[UsersPublic])
async def get_users(session: Session = Depends(get_session)):
    query = select(Users)
    return session.exec(query).all()

@router.get("/{id}", response_model=UsersPublic)
async def get_id_movie(id: int, session: Session = Depends(get_session)):
    user = session.get(Users, id)
    if not user:
        raise HTTPException(status_code=404, detail="Felhasználó nem található")
    return user

@router.post("", status_code=201, response_model=UsersPublic)
async def create_user(user: usersCreate, session: Session = Depends(get_session)):
    db_user = Users.model_validate(user)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Ez az email már foglalt!")
    session.refresh(db_user)
    return db_user

@router.delete("/{id}", status_code=204)
async def deleteUser(id: int, session: Session = Depends(get_session)):
    movie = await get_id_movie(id, session)
    session.delete(movie)
    session.commit()
    return None