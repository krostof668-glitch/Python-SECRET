from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from db import get_session
from models import PostPublic, PostCreate, Post, User

router = APIRouter(prefix="/api", tags=["post"])

@router.get("/post", response_model=list[PostPublic])
async def get_posts(session: Session = Depends(get_session)):
    query = select(Post)
    return session.exec(query).all()

@router.get("/post/{id}", response_model=PostPublic)
async def get_post(id: int, session: Session = Depends(get_session)):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Nincs ilyen jegyzet!")
    return post

@router.post("/user/{id}", response_model=PostPublic, status_code=201)
async def create_post(id: int, post: PostCreate, session: Session = Depends(get_session)):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Nincs ilyen felhasználó")
    
    db_post = Post.model_validate(post, update={"user_id": id})
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    
    return db_post