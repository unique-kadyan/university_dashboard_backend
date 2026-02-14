import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from entities.assessments import Assessment
from entities.grades import Grades
from entities.semester_results import SemesterResults
from enums.result_status import ResultStatus
from repositories.assessment_grade_repository import AssessmentGradeRepository
from schemas.assessment_grade_schemas import (
    AssessmentCreateRequest,
    AssessmentResponse,
    AssessmentUpdateRequest,
    BulkGradeItem,
    BulkGradeRequest,
    BulkGradeResponse,
    BulkGradeResultItem,
    CGPAResponse,
    CourseGradeItem,
    GradeCreateRequest,
    GradeDetailResponse,
    GradeUpdateRequest,
    PublishResultItem,
    PublishResultsRequest,
    PublishResultsResponse,
    SGPAResponse,
    SemesterGPAItem,
)
from schemas.student_schemas import PaginatedResponse


def _percentage_to_grade(percentage: float) -> tuple[float, str]:
    """Convert weighted percentage to grade point (10-point scale) and letter."""
    gp = min(round(percentage / 10, 2), 10.0)
    if percentage >= 90:
        return gp, "O"
    elif percentage >= 80:
        return gp, "A+"
    elif percentage >= 70:
        return gp, "A"
    elif percentage >= 60:
        return gp, "B+"
    elif percentage >= 50:
        return gp, "B"
    elif percentage >= 40:
        return gp, "C"
    else:
        return gp, "F"


class AssessmentService:
    def __init__(self, repo: AssessmentGradeRepository = Depends()):
        self.repo = repo

    async def list_assessments(
        self,
        page: int,
        page_size: int,
        course_offering_id: Optional[int] = None,
        assessment_type: Optional[str] = None,
    ) -> PaginatedResponse[AssessmentResponse]:
        records, total = await self.repo.find_assessments_paginated(
            page=page,
            page_size=page_size,
            course_offering_id=course_offering_id,
            assessment_type=assessment_type,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[AssessmentResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_assessment(
        self, data: AssessmentCreateRequest
    ) -> AssessmentResponse:
        offering = await self.repo.find_course_offering_by_id(data.course_offering_id)
        if not offering:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course offering not found",
            )

        assessment = Assessment(
            course_offering_id=data.course_offering_id,
            name=data.name,
            assessment_type=data.assessment_type,
            description=data.description,
            max_marks=data.max_marks,
            weightage=data.weightage,
            date=data.date,
        )
        try:
            assessment = await self.repo.create_assessment(assessment)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Assessment with this type already exists for this course offering",
            )
        return AssessmentResponse.model_validate(assessment)

    async def get_assessment(self, id: int) -> AssessmentResponse:
        assessment = await self.repo.find_assessment_by_id(id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found",
            )
        return AssessmentResponse.model_validate(assessment)

    async def update_assessment(
        self, id: int, data: AssessmentUpdateRequest
    ) -> AssessmentResponse:
        assessment = await self.repo.find_assessment_by_id(id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        for field, value in update_data.items():
            setattr(assessment, field, value)
        assessment.updated_at = datetime.now(timezone.utc)

        assessment = await self.repo.update_assessment(assessment)
        return AssessmentResponse.model_validate(assessment)

    async def delete_assessment(self, id: int) -> None:
        assessment = await self.repo.find_assessment_by_id(id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found",
            )
        try:
            await self.repo.delete_assessment(assessment)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete assessment with existing grades",
            )


class GradeService:
    def __init__(self, repo: AssessmentGradeRepository = Depends()):
        self.repo = repo

    async def list_grades(
        self,
        page: int,
        page_size: int,
        enrollment_id: Optional[int] = None,
        course_id: Optional[int] = None,
        assessment_id: Optional[int] = None,
        student_id: Optional[int] = None,
    ) -> PaginatedResponse[GradeDetailResponse]:
        records, total = await self.repo.find_grades_paginated(
            page=page,
            page_size=page_size,
            enrollment_id=enrollment_id,
            course_id=course_id,
            assessment_id=assessment_id,
            student_id=student_id,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[GradeDetailResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def submit_grade(
        self, data: GradeCreateRequest, graded_by: str
    ) -> GradeDetailResponse:
        enrollment = await self.repo.find_enrollment_by_id(data.enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )

        assessment = await self.repo.find_assessment_by_id(data.assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found",
            )

        if data.marks_obtained > assessment.max_marks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Marks obtained cannot exceed max marks ({assessment.max_marks})",
            )

        existing = await self.repo.find_grade_by_enrollment_assessment(
            data.enrollment_id, data.assessment_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Grade already submitted for this enrollment and assessment",
            )

        grade = Grades(
            enrollment_id=data.enrollment_id,
            course_id=data.course_id,
            assessment_id=data.assessment_id,
            marks_obtained=data.marks_obtained,
            remarks=data.remarks,
            graded_by=graded_by,
            graded_at=datetime.now(timezone.utc),
        )
        grade = await self.repo.create_grade(grade)
        return GradeDetailResponse.model_validate(grade)

    async def update_grade(
        self, id: int, data: GradeUpdateRequest, graded_by: str
    ) -> GradeDetailResponse:
        grade = await self.repo.find_grade_by_id(id)
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "marks_obtained" in update_data:
            assessment = await self.repo.find_assessment_by_id(grade.assessment_id)
            if assessment and update_data["marks_obtained"] > assessment.max_marks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Marks obtained cannot exceed max marks ({assessment.max_marks})",
                )

        for field, value in update_data.items():
            setattr(grade, field, value)
        grade.graded_by = graded_by
        grade.graded_at = datetime.now(timezone.utc)
        grade.updated_at = datetime.now(timezone.utc)

        grade = await self.repo.update_grade(grade)
        return GradeDetailResponse.model_validate(grade)

    async def bulk_submit_grades(
        self, data: BulkGradeRequest, graded_by: str
    ) -> BulkGradeResponse:
        assessment = await self.repo.find_assessment_by_id(data.assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found",
            )

        results: list[BulkGradeResultItem] = []
        successful = 0
        failed = 0

        for item in data.items:
            result = await self._process_bulk_grade_item(
                item=item,
                assessment=assessment,
                course_id=data.course_id,
                graded_by=graded_by,
            )
            results.append(result)
            if result.success:
                successful += 1
            else:
                failed += 1

        return BulkGradeResponse(
            total=len(data.items),
            successful=successful,
            failed=failed,
            results=results,
        )

    async def _process_bulk_grade_item(
        self,
        item: BulkGradeItem,
        assessment: Assessment,
        course_id: int,
        graded_by: str,
    ) -> BulkGradeResultItem:
        enrollment = await self.repo.find_enrollment_by_id(item.enrollment_id)
        if not enrollment:
            return BulkGradeResultItem(
                enrollment_id=item.enrollment_id,
                success=False,
                message="Enrollment not found",
            )

        if item.marks_obtained > assessment.max_marks:
            return BulkGradeResultItem(
                enrollment_id=item.enrollment_id,
                success=False,
                message=f"Marks exceed max marks ({assessment.max_marks})",
            )

        existing = await self.repo.find_grade_by_enrollment_assessment(
            item.enrollment_id, assessment.id
        )
        if existing:
            return BulkGradeResultItem(
                enrollment_id=item.enrollment_id,
                success=False,
                message="Grade already exists for this assessment",
            )

        grade = Grades(
            enrollment_id=item.enrollment_id,
            course_id=course_id,
            assessment_id=assessment.id,
            marks_obtained=item.marks_obtained,
            remarks=item.remarks,
            graded_by=graded_by,
            graded_at=datetime.now(timezone.utc),
        )
        await self.repo.create_grade(grade)
        return BulkGradeResultItem(
            enrollment_id=item.enrollment_id,
            success=True,
            message="Grade submitted successfully",
        )

    async def calculate_sgpa(self, student_id: int, semester: int) -> SGPAResponse:
        student = await self.repo.find_student_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        rows = await self.repo.get_student_course_grades_for_semester(
            student_id, semester
        )
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No grades found for this student in the given semester",
            )

        courses: list[CourseGradeItem] = []
        total_credits = 0
        weighted_sum = 0.0

        for row in rows:
            pct = float(row["weighted_percentage"] or 0)
            gp, letter = _percentage_to_grade(pct)
            credits = row["credits"]

            courses.append(
                CourseGradeItem(
                    course_id=row["course_id"],
                    course_name=row["course_name"],
                    course_code=row["course_code"],
                    credits=credits,
                    weighted_percentage=round(pct, 2),
                    grade_point=gp,
                    grade_letter=letter,
                )
            )
            total_credits += credits
            weighted_sum += credits * gp

        sgpa = round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0

        return SGPAResponse(
            student_id=student_id,
            semester=semester,
            courses=courses,
            total_credits=total_credits,
            sgpa=sgpa,
        )

    async def calculate_cgpa(self, student_id: int) -> CGPAResponse:
        student = await self.repo.find_student_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        rows = await self.repo.get_semester_results_for_student(student_id)
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No semester results found for this student",
            )

        semesters: list[SemesterGPAItem] = []
        total_credits = 0
        weighted_sum = 0.0

        for row in rows:
            gpa = float(row["gpa"] or 0)
            credits = row["total_credits_attempted"] or 0
            semesters.append(
                SemesterGPAItem(
                    semester=row["semester"],
                    gpa=round(gpa, 2),
                    credits=credits,
                )
            )
            total_credits += credits
            weighted_sum += credits * gpa

        cgpa = round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0

        return CGPAResponse(
            student_id=student_id,
            semesters=semesters,
            total_credits=total_credits,
            cgpa=cgpa,
        )

    async def publish_results(
        self, data: PublishResultsRequest, published_by: str
    ) -> PublishResultsResponse:
        if data.student_ids:
            students = []
            for sid in data.student_ids:
                s = await self.repo.find_student_by_id(sid)
                if s:
                    students.append(s)
        else:
            students = await self.repo.find_students_in_semester(data.semester)

        if not students:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No students found for the given semester",
            )

        results: list[PublishResultItem] = []
        published = 0
        failed = 0

        for student in students:
            result = await self._publish_student_result(
                student_id=student.id,
                semester=data.semester,
                academic_year=data.academic_year,
            )
            results.append(result)
            if result.success:
                published += 1
            else:
                failed += 1

        return PublishResultsResponse(
            total=len(students),
            published=published,
            failed=failed,
            results=results,
        )

    async def _publish_student_result(
        self, student_id: int, semester: int, academic_year: str
    ) -> PublishResultItem:
        rows = await self.repo.get_student_course_grades_for_semester(
            student_id, semester
        )
        if not rows:
            return PublishResultItem(
                student_id=student_id,
                success=False,
                message="No grades found for this semester",
            )

        total_credits = 0
        weighted_sum = 0.0
        credits_earned = 0

        for row in rows:
            pct = float(row["weighted_percentage"] or 0)
            gp, letter = _percentage_to_grade(pct)
            credits = row["credits"]
            total_credits += credits
            weighted_sum += credits * gp
            if letter != "F":
                credits_earned += credits

        gpa = round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0
        result_status = (
            ResultStatus.PASS if credits_earned == total_credits else ResultStatus.FAIL
        )

        enrollment_id = await self.repo.find_enrollment_id_for_student_semester(
            student_id, semester
        )
        if not enrollment_id:
            return PublishResultItem(
                student_id=student_id,
                success=False,
                message="Could not find enrollment for this semester",
            )

        existing_results = await self.repo.get_semester_results_for_student(student_id)
        cgpa_credits = total_credits
        cgpa_sum = total_credits * gpa
        for r in existing_results:
            if r["semester"] != semester:
                c = r["total_credits_attempted"] or 0
                cgpa_credits += c
                cgpa_sum += c * float(r["gpa"] or 0)
        cgpa = round(cgpa_sum / cgpa_credits, 2) if cgpa_credits > 0 else 0.0

        existing = await self.repo.find_semester_result(student_id, semester)
        if existing:
            existing.gpa = Decimal(str(gpa))
            existing.cgpa = Decimal(str(cgpa))
            existing.total_credits_attempted = total_credits
            existing.total_credits_earned = credits_earned
            existing.status = result_status
            existing.updated_at = datetime.now(timezone.utc)
            await self.repo.update_semester_result(existing)
        else:
            sem_result = SemesterResults(
                enrollment_id=enrollment_id,
                student_id=student_id,
                acedamic_year=academic_year,
                semester=semester,
                gpa=Decimal(str(gpa)),
                cgpa=Decimal(str(cgpa)),
                total_credits_attempted=total_credits,
                total_credits_earned=credits_earned,
                status=result_status,
            )
            await self.repo.create_semester_result(sem_result)

        student = await self.repo.find_student_by_id(student_id)
        if student:
            student.cgpa = Decimal(str(cgpa))
            student.updated_at = datetime.now(timezone.utc)
            await self.repo.update_student_cgpa(student)

        return PublishResultItem(
            student_id=student_id,
            success=True,
            message="Results published successfully",
            gpa=gpa,
        )
