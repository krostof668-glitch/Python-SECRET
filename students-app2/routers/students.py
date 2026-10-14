from fastapi import APIRouter, Depends, HTTPException
from models import Students, StudentCreate, PublicStudent
from db import get_session
from sqlmodel import Session, select

router = APIRouter(prefix="/students", tags=["students"])

@router.get("",status_code=200, response_model=list[PublicStudent])
async def get_students(session: Session = Depends(get_session)):
    query = select(Students)
    # query = query.where(Students.name == "Lajcsi")
    data = session.exec(query)
    return data.all()

@router.post("", status_code=201, response_model=PublicStudent)
async def create_student(student: StudentCreate, session: Session = Depends(get_session)):
    db_student = Students.model_validate(student)
    session.add(db_student)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=409, detail="Ez az email már foglalt, béna vagy!")
    session.refresh(db_student)
    return db_student

@router.get("/{id}", response_model=PublicStudent)
async def getStudentByID(id: int, session: Session = Depends(get_session)):
    student = session.get(Students, id)
    if not student:
        raise HTTPException(status_code=404, detail="Nem található ilyen ID!")
    return student

@router.delete("/{id}", status_code=204)
async def deleteStudent(id: int, session: Session = Depends(get_session)):
    student = await getStudentByID(id, session)
    session.delete(student)
    session.commit()
    return None
