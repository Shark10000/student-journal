from typing import Optional
from datetime import date as Date
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

class StudentWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    full_name: str = Field(min_length=2, max_length=120)
    group: str = Field(min_length=1, max_length=40)
    email: str = Field(min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value):
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Некорректный email")
        return value.lower()

class StudentRead(StudentWrite):
    model_config = ConfigDict(from_attributes=True)
    id: int

class StudentPage(BaseModel):
    items: list[StudentRead]
    total: int
    limit: int
    offset: int

class GradeWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    subject: str = Field(min_length=1, max_length=100)
    value: int = Field(ge=2, le=5, strict=True)
    date: Date = Field(default_factory=Date.today)
    comment: str = Field(default="", max_length=500)

class GradeRead(GradeWrite):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int

class AverageRead(BaseModel):
    student_id: int
    subject: Optional[str]
    count: int
    average: Optional[float]
