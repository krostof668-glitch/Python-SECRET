from pydantic import BaseModel

class SubjectType(BaseModel):
    s_name: str
    hours: int
    teacher: str | None = None