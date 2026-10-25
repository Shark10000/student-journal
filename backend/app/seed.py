"""Опциональные демонстрационные данные: python -m app.seed."""
from datetime import date
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import Student, Grade

def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Student.id).limit(1)) is not None:
            print("База уже содержит студентов; заполнение пропущено.")
            return
        for name, group, email, values in [
            ("Анна Смирнова", "ПИ-21", "anna@example.com", [5, 4, 5]),
            ("Михаил Волков", "ПИ-21", "mikhail@example.com", [4, 3, 5]),
            ("София Кузнецова", "ПИ-22", "sofia@example.com", [5, 5, 5]),
            ("Артём Соколов", "ПИ-22", "artem@example.com", [3, 4, 4]),
        ]:
            student = Student(full_name=name, group=group, email=email)
            db.add(student)
            db.flush()
            for subject, value in zip(["Математика", "Программирование", "Базы данных"], values):
                db.add(Grade(student_id=student.id, subject=subject, value=value, date=date.today(), comment="Лабораторная работа"))
        db.commit()
        print("Добавлены 4 студента и 12 оценок.")

if __name__ == "__main__":
    main()
