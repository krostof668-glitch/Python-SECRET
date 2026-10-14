from subject_types import SubjectType
from fastapi import APIRouter, Depends

def common_pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

router = APIRouter(prefix="/subject", tags=["subjects"])
@router.get("/search")
async def get_subject_list(pagination: dict = Depends(common_pagination)):
    return {"pagination": pagination, "subjects": []}

@router.get("")
async def get_subjects(s_name: str | None = None, hour: int | None = None, teacher: str | None = None, pagination: dict = Depends(common_pagination)):
    if not s_name and not hour and not teacher:
        return {"subjects": []}
    return {"pagination": pagination, "s_name": s_name, "hour": hour, "teacher": teacher}

@router.post("", status_code=201)
async def create_subject(subject: SubjectType):
    return subject

@router.get("{id}")
async def get_subject(id: int):
    return {"subject_id": id}