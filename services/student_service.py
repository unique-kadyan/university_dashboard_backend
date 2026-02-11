import csv
import io
import math
import os
import uuid
from datetime import date
from typing import List, Optional
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from passlib.context import CryptContext
from entities.students import Student
from entities.user import User
from repositories.student_repository import StudentRepository
from schemas.student_schemas import (
    AttendanceResponse,
    DocumentResponse,
    EnrollmentResponse,
    FeePaymentResponse,
    GradeResponse,
    PaginatedResponse,
    PhotoUploadResponse,
    StudentAttendanceResponse,
    StudentDocumentsResponse,
    StudentEnrollmentResponse,
    StudentFeesResponse,
    StudentGradesResponse,
    StudentRegisterRequest,
    StudentRegisterResponse,
    StudentResponse,
    StudentSearchResult,
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

    async def get_student_attendance(self, id: int) -> StudentAttendanceResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        records = await self.student_repository.find_attendance_by_student_id(id)
        return StudentAttendanceResponse(
            student_id=student.id,
            user_id=student.user_id,
            attendance=[AttendanceResponse.model_validate(r) for r in records],
        )

    async def get_student_grades(self, id: int) -> StudentGradesResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        grades = await self.student_repository.find_grades_by_student_id(id)
        return StudentGradesResponse(
            student_id=student.id,
            user_id=student.user_id,
            grades=[GradeResponse.model_validate(g) for g in grades],
        )

    async def get_student_fees(self, id: int) -> StudentFeesResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        fees = await self.student_repository.find_fees_by_student_id(id)
        return StudentFeesResponse(
            student_id=student.id,
            user_id=student.user_id,
            fees=[FeePaymentResponse.model_validate(f) for f in fees],
        )

    async def get_student_documents(self, id: int) -> StudentDocumentsResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        documents = await self.student_repository.find_documents_by_user_id(student.user_id)
        return StudentDocumentsResponse(
            student_id=student.id,
            user_id=student.user_id,
            documents=[DocumentResponse.model_validate(d) for d in documents],
        )

    async def search_students(
        self, query: str, limit: int = 20
    ) -> List[StudentSearchResult]:
        rows = await self.student_repository.search_students(query, limit)
        return [
            StudentSearchResult(
                id=row.id,
                user_id=row.user_id,
                Student_id=row.Student_id,
                admisson_number=row.admisson_number,
                first_name=row.first_name,
                last_name=row.last_name,
                email=row.email,
                program_id=row.program_id,
                department_id=row.department_id,
                batch_year=row.batch_year,
                semester=row.semester,
                status=row.status,
            )
            for row in rows
        ]

    EXPORT_COLUMNS = [
        "Student ID", "Admission Number", "First Name", "Last Name",
        "Email", "Phone", "Gender", "Date of Birth", "Program ID",
        "Department ID", "Batch Year", "Semester", "Section", "Category",
        "Nationality", "Blood Group", "Status", "CGPA", "Admission Date",
    ]

    async def export_students(
        self,
        format: str,
        student_status: Optional[str] = None,
        batch_year: Optional[int] = None,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
    ) -> StreamingResponse:
        rows = await self.student_repository.find_all_for_export(
            student_status=student_status,
            batch_year=batch_year,
            department_id=department_id,
            program_id=program_id,
        )

        data = [tuple(str(v) if v is not None else "" for v in row) for row in rows]

        if format == "csv":
            return self._generate_csv(data)
        return self._generate_excel(data)

    def _generate_csv(self, data: list) -> StreamingResponse:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(self.EXPORT_COLUMNS)
        writer.writerows(data)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=students_export.csv"},
        )

    def _generate_excel(self, data: list) -> StreamingResponse:
        wb = Workbook()
        ws = wb.active
        ws.title = "Students"
        ws.append(self.EXPORT_COLUMNS)
        for row in data:
            ws.append(list(row))
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=students_export.xlsx"},
        )

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024

    async def upload_student_photo(
        self, id: int, file: UploadFile
    ) -> PhotoUploadResponse:
        student = await self.student_repository.find_by_id(id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )

        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG, PNG, and WebP images are allowed",
            )

        contents = await file.read()
        if len(contents) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 5 MB",
            )

        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        unique_name = f"{student.user_id}_{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join("uploads", "photos")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(contents)

        user = await self.student_repository.find_user_by_id(student.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.profile_picture and os.path.exists(user.profile_picture):
            os.remove(user.profile_picture)

        await self.student_repository.update_user_profile_picture(user, file_path)

        return PhotoUploadResponse(
            student_id=student.id,
            user_id=student.user_id,
            profile_picture=file_path,
        )
