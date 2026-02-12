from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.assessment_grade_schemas import (
    AssessmentCreateRequest,
    AssessmentResponse,
    AssessmentUpdateRequest,
    BulkGradeRequest,
    BulkGradeResponse,
    CGPAResponse,
    GradeCreateRequest,
    GradeDetailResponse,
    GradeUpdateRequest,
    PublishResultsRequest,
    PublishResultsResponse,
    SGPAResponse,
)
from schemas.student_schemas import PaginatedResponse
from services.assessment_grade_service import AssessmentService, GradeService
from utils.auth_dependency import get_current_user

assessments_router = APIRouter(
    prefix="/api/v1/assessments", tags=["Assessment Management"]
)
grades_router = APIRouter(prefix="/api/v1/grades", tags=["Grade Management"])


@assessments_router.get(
    "/",
    response_model=PaginatedResponse[AssessmentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_assessments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    course_offering_id: Optional[int] = Query(
        None, description="Filter by course offering"
    ),
    assessment_type: Optional[str] = Query(
        None, description="Filter by assessment type"
    ),
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(),
):
    return await service.list_assessments(
        page=page,
        page_size=page_size,
        course_offering_id=course_offering_id,
        assessment_type=assessment_type,
    )


@assessments_router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    data: AssessmentCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can create assessments",
        )
    return await service.create_assessment(data)


@assessments_router.get(
    "/{id}",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_assessment(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(),
):
    return await service.get_assessment(id)


@assessments_router.put(
    "/{id}",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_assessment(
    id: int,
    data: AssessmentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can update assessments",
        )
    return await service.update_assessment(id, data)


@assessments_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_assessment(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: AssessmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete assessments",
        )
    await service.delete_assessment(id)


@grades_router.get(
    "/calculate-sgpa",
    response_model=SGPAResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_sgpa(
    student_id: int = Query(..., description="Student ID"),
    semester: int = Query(..., description="Semester number"),
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    return await service.calculate_sgpa(student_id, semester)


@grades_router.get(
    "/calculate-cgpa",
    response_model=CGPAResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_cgpa(
    student_id: int = Query(..., description="Student ID"),
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    return await service.calculate_cgpa(student_id)


@grades_router.get(
    "/",
    response_model=PaginatedResponse[GradeDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def list_grades(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    enrollment_id: Optional[int] = Query(None, description="Filter by enrollment"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    assessment_id: Optional[int] = Query(None, description="Filter by assessment"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    return await service.list_grades(
        page=page,
        page_size=page_size,
        enrollment_id=enrollment_id,
        course_id=course_id,
        assessment_id=assessment_id,
        student_id=student_id,
    )


@grades_router.post(
    "/",
    response_model=GradeDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_grade(
    data: GradeCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can submit grades",
        )
    return await service.submit_grade(data, graded_by=current_user["id"])


@grades_router.put(
    "/{id}",
    response_model=GradeDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def update_grade(
    id: int,
    data: GradeUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can update grades",
        )
    return await service.update_grade(id, data, graded_by=current_user["id"])


@grades_router.post(
    "/bulk",
    response_model=BulkGradeResponse,
    status_code=status.HTTP_200_OK,
)
async def bulk_submit_grades(
    data: BulkGradeRequest,
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can submit grades",
        )
    return await service.bulk_submit_grades(data, graded_by=current_user["id"])


@grades_router.post(
    "/publish",
    response_model=PublishResultsResponse,
    status_code=status.HTTP_200_OK,
)
async def publish_results(
    data: PublishResultsRequest,
    current_user: dict = Depends(get_current_user),
    service: GradeService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can publish results",
        )
    return await service.publish_results(data, published_by=current_user["id"])
