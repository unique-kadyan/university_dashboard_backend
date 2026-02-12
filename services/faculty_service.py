import math
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, UploadFile, status
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from entities.faculty import Faculty
from entities.user import User
from repositories.faculty_repository import FacultyRepository
from schemas.faculty_schemas import (
    FacultyCourseResponse,
    FacultyPhotoUploadResponse,
    FacultyRegisterRequest,
    FacultyRegisterResponse,
    FacultyResponse,
    FacultyScheduleResponse,
    FacultyStudentResponse,
    FacultyUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class FacultyService:
    def __init__(self, faculty_repository: FacultyRepository = Depends()):
        self.faculty_repository = faculty_repository

    async def get_all_faculty(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        employment_type: Optional[str] = None,
        is_hod: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[FacultyResponse]:
        faculty_list, total = await self.faculty_repository.find_all_paginated(
            page=page,
            page_size=page_size,
            status=status,
            department_id=department_id,
            employment_type=employment_type,
            is_hod=is_hod,
            search=search,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedResponse(
            items=[FacultyResponse.model_validate(f) for f in faculty_list],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_faculty(
        self, data: FacultyRegisterRequest
    ) -> FacultyRegisterResponse:
        existing_email = await self.faculty_repository.find_user_by_email(data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        existing_username = await self.faculty_repository.find_user_by_username(
            data.user_name
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        existing_employee = await self.faculty_repository.find_faculty_by_employee_id(
            data.employee_id
        )
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID already exists",
            )

        existing_faculty = await self.faculty_repository.find_faculty_by_id(
            data.faculty_id
        )
        if existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Faculty ID already exists",
            )

        department = await self.faculty_repository.find_department_by_code(
            data.department_code
        )
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with code '{data.department_code}' not found",
            )

        user = User(
            user_type="faculty",
            email=data.email,
            user_name=data.user_name,
            hashed_password=pwd_context.hash(data.password),
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            phone=data.phone,
            emergency_contact=data.emergency_contact,
            address=data.address,
            city=data.city,
            state=data.state,
            country=data.country,
            postal_code=data.postal_code,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
        )
        user = await self.faculty_repository.create_user(user)

        faculty = Faculty(
            id=data.faculty_id,
            user_id=user.id,
            employee_id=data.employee_id,
            department_id=department.id,
            designation=data.designation,
            specialization=data.specialization,
            qualification=data.qualification,
            date_of_joining=data.date_of_joining,
            employment_type=data.employment_type,
            experience_years=data.experience_years,
            is_hod=data.is_hod,
            status=data.status,
            created_at=datetime.now(timezone.utc),
        )
        faculty = await self.faculty_repository.create_faculty(faculty)

        return FacultyRegisterResponse(
            user_id=user.id,
            email=user.email,
            user_name=user.user_name,
            first_name=user.first_name,
            last_name=user.last_name,
            id=faculty.id,
            employee_id=faculty.employee_id,
            department_id=faculty.department_id,
            designation=faculty.designation,
            employment_type=faculty.employment_type,
            status=faculty.status,
        )

    async def get_faculty_by_id(self, id: str) -> FacultyResponse:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )
        return FacultyResponse.model_validate(faculty)

    async def update_faculty(
        self, id: str, data: FacultyUpdateRequest
    ) -> FacultyResponse:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        for field, value in update_data.items():
            setattr(faculty, field, value)
        faculty.updated_at = datetime.now(timezone.utc)

        faculty = await self.faculty_repository.update_faculty(faculty)
        return FacultyResponse.model_validate(faculty)

    async def delete_faculty(self, id: str) -> None:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )

        user = await self.faculty_repository.find_user_by_id(faculty.user_id)
        try:
            await self.faculty_repository.delete_faculty(faculty)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete faculty with existing related records (courses, attendance, etc.)",
            )
        if user:
            try:
                await self.faculty_repository.delete_user(user)
            except IntegrityError:
                pass

    async def get_faculty_courses(self, id: str) -> list[FacultyCourseResponse]:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )
        rows = await self.faculty_repository.find_courses_by_faculty_id(id)
        return [FacultyCourseResponse(**row) for row in rows]

    async def get_faculty_schedule(self, id: str) -> list[FacultyScheduleResponse]:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )
        rows = await self.faculty_repository.find_schedule_by_faculty_id(id)
        return [FacultyScheduleResponse(**row) for row in rows]

    async def get_faculty_students(self, id: str) -> list[FacultyStudentResponse]:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )
        rows = await self.faculty_repository.find_students_by_faculty_id(id)
        return [FacultyStudentResponse(**row) for row in rows]

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024

    async def upload_faculty_photo(
        self, id: str, file: UploadFile
    ) -> FacultyPhotoUploadResponse:
        faculty = await self.faculty_repository.find_faculty_by_id(id)
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found",
            )

        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG, PNG, and WebP images are allowed",
            )

        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .jpg, .jpeg, .png, and .webp file extensions are allowed",
            )

        contents = await file.read()
        if len(contents) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 5 MB",
            )

        unique_name = f"{faculty.user_id}_{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join("uploads", "photos")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(contents)

        user = await self.faculty_repository.find_user_by_id(faculty.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.profile_picture and os.path.exists(user.profile_picture):
            os.remove(user.profile_picture)

        await self.faculty_repository.update_user_profile_picture(user, file_path)

        return FacultyPhotoUploadResponse(
            faculty_id=faculty.id,
            user_id=faculty.user_id,
            profile_picture=file_path,
        )
