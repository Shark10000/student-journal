from typing import Optional
from typing import Literal
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student, Grade
from ..schemas import StudentWrite, StudentRead, StudentPage, AverageRead
from .. import crud

router = APIRouter(prefix="/students", tags=["Студенты"])

@router.get("", response_model=StudentPage)
def list_students(q: str = Query("", max_length=120), group: Optional[str] = None,
                  sort: Literal["full_name", "group", "id"] = "full_name",
                  order: Literal["asc", "desc"] = "asc",
                  limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0),
                  db: Session = Depends(get_db)):
    filters = []
    if q.strip():
        filters.append(Student.full_name.icontains(q.strip(), autoescape=True))
    if group:
        filters.append(Student.group == group)
    total = db.scalar(select(func.count()).select_from(Student).where(*filters))
    column = getattr(Student, sort)
    stmt = select(Student).where(*filters).order_by(column.desc() if order == "desc" else column.asc(), Student.id).offset(offset).limit(limit)
    return {"items": db.scalars(stmt).all(), "total": total, "limit": limit, "offset": offset}

@router.post("", response_model=StudentRead, status_code=201)
def create_student(data: StudentWrite, db: Session = Depends(get_db)):
    return crud.save(db, Student(**data.model_dump()))

@router.get("/{student_id}", response_model=StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    return crud.get_student(db, student_id)

@router.put("/{student_id}", response_model=StudentRead)
def update_student(student_id: int, data: StudentWrite, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    for key, value in data.model_dump().items():
        setattr(student, key, value)
    return crud.save(db, student)

@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db.delete(crud.get_student(db, student_id))
    db.commit()
    return Response(status_code=204)

@router.get("/{student_id}/average", response_model=AverageRead)
def average(student_id: int, subject: Optional[str] = None, db: Session = Depends(get_db)):
    crud.get_student(db, student_id)
    stmt = select(func.count(Grade.id), func.avg(Grade.value)).where(Grade.student_id == student_id)
    if subject:
        stmt = stmt.where(Grade.subject == subject)
    count, value = db.execute(stmt).one()
    return {"student_id": student_id, "subject": subject, "count": count, "average": round(value, 2) if value is not None else None}
