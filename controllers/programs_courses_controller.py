from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.program_course_schemas import (
    CourseCreateRequest,
    CourseOfferingCreateRequest,
    CourseOfferingResponse,
    CourseOfferingUpdateRequest,
    CoursePrerequisiteResponse,
    CourseResponse,
    CourseUpdateRequest,
    ProgramCourseItem,
    ProgramCreateRequest,
    ProgramResponse,
    ProgramUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse
from services.program_course_service import (
    CourseOfferingService,
    CourseService,
    ProgramService,
)
from utils.auth_dependency import get_current_user

programs_router = APIRouter(prefix="/api/v1/programs", tags=["Programs"])


@programs_router.get(
    "/",
    response_model=PaginatedResponse[ProgramResponse],
    status_code=status.HTTP_200_OK,
)
async def get_programs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    degree_type: Optional[str] = Query(None, description="Filter by degree type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    current_user: dict = Depends(get_current_user),
    program_service: ProgramService = Depends(),
):
    return await program_service.get_all_programs(
        page=page,
        page_size=page_size,
        department_id=department_id,
        degree_type=degree_type,
        is_active=is_active,
        search=search,
    )


@programs_router.post(
    "/",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_program(
    program_data: ProgramCreateRequest,
    current_user: dict = Depends(get_current_user),
    program_service: ProgramService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create programs",
        )
    return await program_service.create_program(program_data)


@programs_router.get(
    "/{id}",
    response_model=ProgramResponse,
    status_code=status.HTTP_200_OK,
)
async def get_program_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    program_service: ProgramService = Depends(),
):
    return await program_service.get_program_by_id(id)


@programs_router.put(
    "/{id}",
    response_model=ProgramResponse,
    status_code=status.HTTP_200_OK,
)
async def update_program(
    id: int,
    program_data: ProgramUpdateRequest,
    current_user: dict = Depends(get_current_user),
    program_service: ProgramService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update programs",
        )
    return await program_service.update_program(id, program_data)


@programs_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    id: int,
    current_user: dict = Depends(get_current_user),
    program_service: ProgramService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete programs",
        )
    await program_service.delete_program(id)


@programs_router.get(
    "/{id}/courses",
    response_model=list[ProgramCourseItem],
    status_code=status.HTTP_200_OK,
)
async def get_program_courses(
    id: int,
    current_user: dict = Depends(get_current_user),
    program_service: ProgramService = Depends(),
):
    return await program_service.get_program_courses(id)


courses_router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@courses_router.get(
    "/",
    response_model=PaginatedResponse[CourseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_courses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    course_type: Optional[str] = Query(None, description="Filter by course type"),
    level: Optional[str] = Query(None, description="Filter by level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(),
):
    return await course_service.get_all_courses(
        page=page,
        page_size=page_size,
        department_id=department_id,
        course_type=course_type,
        level=level,
        is_active=is_active,
        search=search,
    )


@courses_router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
    course_data: CourseCreateRequest,
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create courses",
        )
    return await course_service.create_course(course_data)


@courses_router.get(
    "/{id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
)
async def get_course_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(),
):
    return await course_service.get_course_by_id(id)


@courses_router.put(
    "/{id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
)
async def update_course(
    id: int,
    course_data: CourseUpdateRequest,
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update courses",
        )
    return await course_service.update_course(id, course_data)


@courses_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    id: int,
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete courses",
        )
    await course_service.delete_course(id)


@courses_router.get(
    "/{id}/prerequisites",
    response_model=list[CoursePrerequisiteResponse],
    status_code=status.HTTP_200_OK,
)
async def get_course_prerequisites(
    id: int,
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(),
):
    return await course_service.get_course_prerequisites(id)


offerings_router = APIRouter(
    prefix="/api/v1/course-offerings", tags=["Course Offerings"]
)


@offerings_router.get(
    "/",
    response_model=PaginatedResponse[CourseOfferingResponse],
    status_code=status.HTTP_200_OK,
)
async def get_offerings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    program_id: Optional[int] = Query(None, description="Filter by program"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    acedemic_year: Optional[str] = Query(None, description="Filter by academic year"),
    offering_status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
    offering_service: CourseOfferingService = Depends(),
):
    return await offering_service.get_all_offerings(
        page=page,
        page_size=page_size,
        program_id=program_id,
        course_id=course_id,
        semester=semester,
        acedemic_year=acedemic_year,
        offering_status=offering_status,
    )


@offerings_router.post(
    "/",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_offering(
    offering_data: CourseOfferingCreateRequest,
    current_user: dict = Depends(get_current_user),
    offering_service: CourseOfferingService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create course offerings",
        )
    return await offering_service.create_offering(offering_data)


@offerings_router.get(
    "/{id}",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_offering_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    offering_service: CourseOfferingService = Depends(),
):
    return await offering_service.get_offering_by_id(id)


@offerings_router.put(
    "/{id}",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_200_OK,
)
async def update_offering(
    id: int,
    offering_data: CourseOfferingUpdateRequest,
    current_user: dict = Depends(get_current_user),
    offering_service: CourseOfferingService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update course offerings",
        )
    return await offering_service.update_offering(id, offering_data)


@offerings_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offering(
    id: int,
    current_user: dict = Depends(get_current_user),
    offering_service: CourseOfferingService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete course offerings",
        )
    await offering_service.delete_offering(id)
