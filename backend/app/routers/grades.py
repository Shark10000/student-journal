from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Grade
from ..schemas import GradeWrite, GradeRead
from .. import crud

router = APIRouter(tags=["Оценки"])

@router.get("/students/{student_id}/grades", response_model=list[GradeRead])
def list_grades(student_id: int, subject: Optional[str] = None,
                limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0),
                db: Session = Depends(get_db)):
    crud.get_student(db, student_id)
    stmt = select(Grade).where(Grade.student_id == student_id)
    if subject:
        stmt = stmt.where(Grade.subject == subject)
    return db.scalars(stmt.order_by(Grade.date.desc(), Grade.id.desc()).limit(limit).offset(offset)).all()

@router.post("/students/{student_id}/grades", response_model=GradeRead, status_code=201)
def create_grade(student_id: int, data: GradeWrite, db: Session = Depends(get_db)):
    crud.get_student(db, student_id)
    return crud.save(db, Grade(student_id=student_id, **data.model_dump()))

@router.get("/grades/{grade_id}", response_model=GradeRead)
def read_grade(grade_id: int, db: Session = Depends(get_db)):
    return crud.get_grade(db, grade_id)

@router.put("/grades/{grade_id}", response_model=GradeRead)
def update_grade(grade_id: int, data: GradeWrite, db: Session = Depends(get_db)):
    grade = crud.get_grade(db, grade_id)
    for key, value in data.model_dump().items():
        setattr(grade, key, value)
    return crud.save(db, grade)

@router.delete("/grades/{grade_id}", status_code=204)
def delete_grade(grade_id: int, db: Session = Depends(get_db)):
    db.delete(crud.get_grade(db, grade_id))
    db.commit()
    return Response(status_code=204)
