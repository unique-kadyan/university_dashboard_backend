import math
from datetime import date
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from entities.students import Student
from entities.user import User
from repositories.student_repository import StudentRepository
from schemas.student_schemas import (
    EnrollmentResponse,
    PaginatedResponse,
    StudentEnrollmentResponse,
    StudentRegisterRequest,
    StudentRegisterResponse,
    StudentResponse,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class StudentService:
    def __init__(self, student_repository: StudentRepository = Depends()):
        self.student_repository = student_repository

    async def get_all_students(
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
    ) -> PaginatedResponse[StudentResponse]:
        students, total = await self.student_repository.find_all_paginated(
            page=page,
            page_size=page_size,
            status=status,
            department_id=department_id,
            program_id=program_id,
            batch_year=batch_year,
            semester=semester,
            category=category,
            search=search,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedResponse(
            items=[StudentResponse.model_validate(s) for s in students],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_student(
        self, student_data: StudentRegisterRequest
    ) -> StudentRegisterResponse:
        existing_email = await self.student_repository.find_user_by_email(
            student_data.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        existing_username = await self.student_repository.find_user_by_username(
            student_data.user_name
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        existing_student_id = await self.student_repository.find_student_by_student_id(
            student_data.Student_id
        )
        if existing_student_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student ID already exists",
            )

        existing_admission = (
            await self.student_repository.find_student_by_admission_number(
                student_data.admisson_number
            )
        )
        if existing_admission:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Admission number already exists",
            )

        program = await self.student_repository.find_program_by_code(
            student_data.program_code
        )
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with code '{student_data.program_code}' not found",
            )

        department = await self.student_repository.find_department_by_code(
            student_data.department_code
        )
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with code '{student_data.department_code}' not found",
            )

        hashed_password = pwd_context.hash(student_data.password)
        user = User(
            user_type="student",
            email=student_data.email,
            user_name=student_data.user_name,
            hashed_password=hashed_password,
            first_name=student_data.first_name,
            middle_name=student_data.middle_name,
            last_name=student_data.last_name,
            date_of_birth=student_data.date_of_birth,
            gender=student_data.gender.value if student_data.gender else None,
            phone=student_data.phone,
            emergency_contact=student_data.emergency_contact,
            address=student_data.address,
            city=student_data.city,
            state=student_data.state,
            country=student_data.country,
            postal_code=student_data.postal_code,
            is_active=True,
            is_verified=False,
            created_at=date.today(),
        )
        created_user = await self.student_repository.create_user(user)

        student = Student(
            user_id=created_user.id,
            Student_id=student_data.Student_id,
            admisson_number=student_data.admisson_number,
            admission_date=student_data.admission_date,
            program_id=program.id,
            department_id=department.id,
            batch_year=student_data.batch_year,
            semester=student_data.semester,
            section=student_data.section,
            blood_group=student_data.blood_group,
            nationality=student_data.nationality,
            religion=student_data.religion,
            category=student_data.category.value if student_data.category else None,
            status=student_data.status.value,
        )
        created_student = await self.student_repository.create_student(student)

        return StudentRegisterResponse(
            user_id=created_user.id,
            email=created_user.email,
            user_name=created_user.user_name,
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            id=created_student.id,
            Student_id=created_student.Student_id,
            admisson_number=created_student.admisson_number,
            admission_date=created_student.admission_date,
            program_id=created_student.program_id,
            department_id=created_student.department_id,
            batch_year=created_student.batch_year,
            semester=created_student.semester,
            status=created_student.status,
        )

    async def get_student_by_id(self, id: int) -> StudentResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        return StudentResponse.model_validate(student)

    async def update_student(
        self, id: int, student_data: StudentRegisterRequest
    ) -> StudentResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )

        student.Student_id = student_data.Student_id
        student.admisson_number = student_data.admisson_number
        student.admission_date = student_data.admission_date
        student.batch_year = student_data.batch_year
        student.semester = student_data.semester
        student.section = student_data.section
        student.blood_group = student_data.blood_group
        student.nationality = student_data.nationality
        student.religion = student_data.religion
        student.category = (
            student_data.category.value if student_data.category else None
        )
        student.status = student_data.status.value
        updated_student = await self.student_repository.update_student(student)
        return StudentResponse.model_validate(updated_student)

    async def delete_student(self, id: int):
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        await self.student_repository.delete_student(student)
        student = await self.student_repository.find_by_id(id)
        if student and student.is_active is not False:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete student",
            )
        else:
            return {"detail": "Student deleted successfully"}

    async def get_student_enrollments(self, id: int) -> StudentEnrollmentResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        enrollments = await self.student_repository.find_enrollments_by_student_id(id)
        return StudentEnrollmentResponse(
            student_id=student.id,
            user_id=student.user_id,
            enrollments=[EnrollmentResponse.model_validate(e) for e in enrollments],
        )
