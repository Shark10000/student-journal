from datetime import date
from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), index=True)
    group: Mapped[str] = mapped_column(String(40), index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    grades: Mapped[list["Grade"]] = relationship(back_populates="student", cascade="all, delete-orphan")

class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (CheckConstraint("value >= 2 AND value <= 5"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    subject: Mapped[str] = mapped_column(String(100), index=True)
    value: Mapped[int]
    date: Mapped[date]
    comment: Mapped[str] = mapped_column(String(500), default="")
    student: Mapped[Student] = relationship(back_populates="grades")
