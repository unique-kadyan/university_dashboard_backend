import math
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from entities.enrollments import Enrollment
from enums.student_status import StudentStatus
from enums.status import Status
from repositories.enrollment_repository import EnrollmentRepository
from schemas.enrollment_schemas import (
    BulkEnrollmentItem,
    BulkEnrollmentRequest,
    BulkEnrollmentResponse,
    BulkEnrollmentResultItem,
    EligibilityResponse,
    EnrollmentCreateRequest,
    EnrollmentResponse,
    EnrollmentUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse


class EnrollmentService:
    def __init__(self, repo: EnrollmentRepository = Depends()):
        self.repo = repo

    async def get_all_enrollments(
        self,
        page: int,
        page_size: int,
        student_id: Optional[int] = None,
        program_id: Optional[int] = None,
        enrollment_status: Optional[str] = None,
    ) -> PaginatedResponse[EnrollmentResponse]:
        enrollments, total = await self.repo.find_enrollments_paginated(
            page=page,
            page_size=page_size,
            student_id=student_id,
            program_id=program_id,
            status=enrollment_status,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[EnrollmentResponse.model_validate(e) for e in enrollments],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_enrollment(
        self, data: EnrollmentCreateRequest
    ) -> EnrollmentResponse:
        student = await self.repo.find_student_by_id(data.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        program = await self.repo.find_program_by_id(data.program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )

        if not program.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Program is not active",
            )

        existing = await self.repo.find_existing_enrollment(
            data.student_id, data.program_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student is already enrolled in this program",
            )

        enrollment = Enrollment(
            student_id=data.student_id,
            program_id=data.program_id,
            enrollment_date=data.enrollment_date,
            status=StudentStatus.ENROLLED,
            remarks=data.remarks,
            created_at=datetime.now(timezone.utc),
        )
        enrollment = await self.repo.create_enrollment(enrollment)
        return EnrollmentResponse.model_validate(enrollment)

    async def get_enrollment_by_id(self, id: int) -> EnrollmentResponse:
        enrollment = await self.repo.find_enrollment_by_id(id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )
        return EnrollmentResponse.model_validate(enrollment)

    async def update_enrollment(
        self, id: int, data: EnrollmentUpdateRequest
    ) -> EnrollmentResponse:
        enrollment = await self.repo.find_enrollment_by_id(id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        for field, value in update_data.items():
            setattr(enrollment, field, value)
        enrollment.updated_at = datetime.now(timezone.utc)

        enrollment = await self.repo.update_enrollment(enrollment)
        return EnrollmentResponse.model_validate(enrollment)

    async def delete_enrollment(self, id: int) -> None:
        enrollment = await self.repo.find_enrollment_by_id(id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )
        try:
            await self.repo.delete_enrollment(enrollment)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete enrollment with existing related records",
            )

    async def bulk_enroll(self, data: BulkEnrollmentRequest) -> BulkEnrollmentResponse:
        results: list[BulkEnrollmentResultItem] = []
        successful = 0
        failed = 0

        for item in data.enrollments:
            result = await self._process_single_enrollment(item)
            results.append(result)
            if result.success:
                successful += 1
            else:
                failed += 1

        return BulkEnrollmentResponse(
            total=len(data.enrollments),
            successful=successful,
            failed=failed,
            results=results,
        )

    async def _process_single_enrollment(
        self, item: BulkEnrollmentItem
    ) -> BulkEnrollmentResultItem:
        student = await self.repo.find_student_by_id(item.student_id)
        if not student:
            return BulkEnrollmentResultItem(
                student_id=item.student_id,
                program_id=item.program_id,
                success=False,
                message="Student not found",
            )

        program = await self.repo.find_program_by_id(item.program_id)
        if not program:
            return BulkEnrollmentResultItem(
                student_id=item.student_id,
                program_id=item.program_id,
                success=False,
                message="Program not found",
            )

        if not program.is_active:
            return BulkEnrollmentResultItem(
                student_id=item.student_id,
                program_id=item.program_id,
                success=False,
                message="Program is not active",
            )

        existing = await self.repo.find_existing_enrollment(
            item.student_id, item.program_id
        )
        if existing:
            return BulkEnrollmentResultItem(
                student_id=item.student_id,
                program_id=item.program_id,
                success=False,
                message="Student is already enrolled in this program",
            )

        enrollment = Enrollment(
            student_id=item.student_id,
            program_id=item.program_id,
            enrollment_date=item.enrollment_date,
            status=StudentStatus.ENROLLED,
            remarks=item.remarks,
            created_at=datetime.now(timezone.utc),
        )
        enrollment = await self.repo.create_enrollment(enrollment)
        return BulkEnrollmentResultItem(
            student_id=item.student_id,
            program_id=item.program_id,
            success=True,
            message="Enrolled successfully",
            enrollment_id=enrollment.id,
        )

    async def verify_eligibility(
        self, student_id: int, program_id: int
    ) -> EligibilityResponse:
        reasons: list[str] = []

        student = await self.repo.find_student_by_id(student_id)
        if not student:
            return EligibilityResponse(
                student_id=student_id,
                program_id=program_id,
                is_eligible=False,
                reasons=["Student not found"],
            )

        program = await self.repo.find_program_by_id(program_id)
        if not program:
            return EligibilityResponse(
                student_id=student_id,
                program_id=program_id,
                is_eligible=False,
                reasons=["Program not found"],
            )

        if not program.is_active:
            reasons.append("Program is not active")

        if student.status != Status.ACTIVE:
            reasons.append("Student is not in active status")

        existing = await self.repo.find_existing_enrollment(student_id, program_id)
        if existing:
            reasons.append("Student is already enrolled in this program")

        is_eligible = len(reasons) == 0
        if is_eligible:
            reasons.append("Student is eligible for enrollment")

        return EligibilityResponse(
            student_id=student_id,
            program_id=program_id,
            is_eligible=is_eligible,
            reasons=reasons,
        )
