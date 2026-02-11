from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.students import Student
from entities.attendance import Attendance
from entities.enrollments import Enrollment
from entities.documents import Document
from entities.fee_payments import FeePayment
from entities.grades import Grades
from entities.user import User
from entities.programs import Program
from entities.departments import Department


class StudentRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_program_by_code(self, code: str) -> Program | None:
        result = await self.db.execute(select(Program).where(Program.code == code))
        return result.scalar_one_or_none()

    async def find_department_by_code(self, code: str) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.code == code)
        )
        return result.scalar_one_or_none()

    async def find_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def find_user_by_username(self, user_name: str) -> User | None:
        result = await self.db.execute(select(User).where(User.user_name == user_name))
        return result.scalar_one_or_none()

    async def find_student_by_student_id(self, student_id: str) -> Student | None:
        result = await self.db.execute(
            select(Student).where(Student.Student_id == student_id)
        )
        return result.scalar_one_or_none()

    async def find_student_by_admission_number(
        self, admisson_number: str
    ) -> Student | None:
        result = await self.db.execute(
            select(Student).where(Student.admisson_number == admisson_number)
        )
        return result.scalar_one_or_none()

    async def find_by_id(self, id: int) -> Student | None:
        result = await self.db.execute(select(Student).where(Student.id == id))
        return result.scalar_one_or_none()

    async def find_enrollments_by_student_id(self, student_id: int) -> List[Enrollment]:
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.student_id == student_id)
        )
        return list(result.scalars().all())

    async def find_attendance_by_student_id(self, student_id: int) -> List[Attendance]:
        result = await self.db.execute(
            select(Attendance).where(Attendance.student_id == student_id)
        )
        return list(result.scalars().all())

    async def find_grades_by_student_id(self, student_id: int) -> List[Grades]:
        result = await self.db.execute(
            select(Grades)
            .join(Enrollment, Grades.enrollment_id == Enrollment.id)
            .where(Enrollment.student_id == student_id)
        )
        return list(result.scalars().all())

    async def find_fees_by_student_id(self, student_id: int) -> List[FeePayment]:
        result = await self.db.execute(
            select(FeePayment).where(FeePayment.student_id == student_id)
        )
        return list(result.scalars().all())

    async def find_documents_by_user_id(self, user_id: int) -> List[Document]:
        result = await self.db.execute(
            select(Document).where(Document.uploaded_by == user_id)
        )
        return list(result.scalars().all())

    async def find_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_user_profile_picture(self, user: User, file_path: str) -> User:
        user.profile_picture = file_path
        await self.db.merge(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def create_student(self, student: Student) -> Student:
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def find_all_paginated(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
        batch_year: Optional[int] = None,
        semester: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Student], int]:
        query = select(Student)
        count_query = select(func.count()).select_from(Student)

        if status:
            query = query.where(Student.status == status)
            count_query = count_query.where(Student.status == status)

        if department_id:
            query = query.where(Student.department_id == department_id)
            count_query = count_query.where(Student.department_id == department_id)

        if program_id:
            query = query.where(Student.program_id == program_id)
            count_query = count_query.where(Student.program_id == program_id)

        if batch_year:
            query = query.where(Student.batch_year == batch_year)
            count_query = count_query.where(Student.batch_year == batch_year)

        if semester:
            query = query.where(Student.semester == semester)
            count_query = count_query.where(Student.semester == semester)

        if category:
            query = query.where(Student.category == category)
            count_query = count_query.where(Student.category == category)

        if search:
            search_filter = Student.Student_id.ilike(
                f"%{search}%"
            ) | Student.admisson_number.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Student.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        return students, total

    async def search_students(self, query: str, limit: int = 20) -> list:
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(
                Student.id,
                Student.user_id,
                Student.Student_id,
                Student.admisson_number,
                User.first_name,
                User.last_name,
                User.email,
                Student.program_id,
                Student.department_id,
                Student.batch_year,
                Student.semester,
                Student.status,
            )
            .join(User, Student.user_id == User.id)
            .where(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    Student.Student_id.ilike(search_term),
                    Student.admisson_number.ilike(search_term),
                )
            )
            .order_by(Student.id)
            .limit(limit)
        )
        return list(result.all())

    async def find_all_for_export(
        self,
        student_status: Optional[str] = None,
        batch_year: Optional[int] = None,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
    ) -> list:
        query = select(
            Student.Student_id,
            Student.admisson_number,
            User.first_name,
            User.last_name,
            User.email,
            User.phone,
            User.gender,
            User.date_of_birth,
            Student.program_id,
            Student.department_id,
            Student.batch_year,
            Student.semester,
            Student.section,
            Student.category,
            Student.nationality,
            Student.blood_group,
            Student.status,
            Student.cgpa,
            Student.admission_date,
        ).join(User, Student.user_id == User.id)

        if student_status:
            query = query.where(Student.status == student_status)
        if batch_year:
            query = query.where(Student.batch_year == batch_year)
        if department_id:
            query = query.where(Student.department_id == department_id)
        if program_id:
            query = query.where(Student.program_id == program_id)

        query = query.order_by(Student.id)
        result = await self.db.execute(query)
        return list(result.all())

    async def update_student(self, student: Student) -> Student:
        await self.db.merge(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def delete_student(self, student: Student) -> None:
        student.is_active = False
        await self.db.merge(student)
        await self.db.commit()
        await self.db.refresh(student)
