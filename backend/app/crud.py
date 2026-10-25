from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Student, Grade


def get_student(db: Session, student_id: int):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(404, "Студент не найден")
    return student


def get_grade(db: Session, grade_id: int):
    grade = db.get(Grade, grade_id)
    if grade is None:
        raise HTTPException(404, "Оценка не найдена")
    return grade


def save(db: Session, entity):
    db.add(entity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Студент с таким email уже существует")
    db.refresh(entity)
    return entity
