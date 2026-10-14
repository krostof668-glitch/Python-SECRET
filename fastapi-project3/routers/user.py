from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from db import get_session
from models import User, UserPublic, CreateUser, Post, PostPublic
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api", tags=["user"])

@router.get("/user", response_model=list[UserPublic], status_code=200)
async def get_users(name: str | None = Query(default=None, description="Név szerinti szűrés"), salary: int | None = Query(default=None, description="Fizetés szerint"), session: Session = Depends(get_session)):
    query = select(User)
    if name:
        query = query.where(User.name.icontains(name))
    if salary:
        query = query.where(User.salary == salary)
    users = session.exec(query).all()
    return users

@router.get("/user/{id}", response_model=list[PostPublic])
async def get_user_by_id(
    id: int, 
    title: str | None = Query(default=None, description="Keresés cím alapján"),
    content: str | None = Query(default=None, description="Keresés tartalom alapján"),
    session: Session = Depends(get_session)) -> list[PostPublic]:
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=400, detail="Nincs ilyen felhasználó")
    query = select(Post).where(Post.user_id == id)
    if title:
        query = query.where(Post.title.icontains(title))
    if content:
        query = query.where(Post.content.icontains(content))
    return session.exec(query).all()


@router.post("/user", response_model=UserPublic, status_code=201)
async def create_user(user: CreateUser, session: Session = Depends(get_session)):
    user_db = User.model_validate(user)
    session.add(user_db)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Ez az email-cím már foglalt.")
    session.refresh(user_db)
    return user_db

