import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import uvicorn

from configs.db_config import create_schema, create_tables, engine
from gateway import setup_gateway

from controllers.authentication_authroziation_controller import router as auth_router
from controllers.students_management_controller import router as students_router
from controllers.faculty_management_controller import router as faculty_router
from controllers.department_management_controller import router as department_router
from controllers.programs_courses_controller import (
    programs_router,
    courses_router,
    offerings_router,
)
from controllers.enrollment_management_controller import router as enrollment_router
from controllers.attendance_management_controller import router as attendance_router
from controllers.assessments_grades_controller import (
    assessments_router,
    grades_router,
)
from controllers.fees_management_controller import (
    fee_structures_router,
    fee_payments_router,
)
from controllers.library_management_controllers import library_router
from controllers.hostel_management_controller import (
    hostels_router,
    hostel_rooms_router,
    hostel_allocations_router,
)
from controllers.examination_management_controller import (
    exam_schedules_router,
    exam_timetable_router,
)
from controllers.timetable_management import timetable_router
from controllers.notification_management_controller import notification_router
from controllers.document_management_controller import document_router
from controllers.reports_analytics_controller import reports_router, analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_schema()
    await create_tables()
    yield
    await engine.dispose()


app = FastAPI(
    title="Student Management System",
    description="API for managing students, courses, exams, and more",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

setup_gateway(app, log_level=os.getenv("LOG_LEVEL", "INFO"))


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth_router)
app.include_router(students_router)
app.include_router(faculty_router)
app.include_router(department_router)
app.include_router(programs_router)
app.include_router(courses_router)
app.include_router(offerings_router)
app.include_router(enrollment_router)
app.include_router(attendance_router)
app.include_router(assessments_router)
app.include_router(grades_router)
app.include_router(fee_structures_router)
app.include_router(fee_payments_router)
app.include_router(library_router)
app.include_router(hostels_router)
app.include_router(hostel_rooms_router)
app.include_router(hostel_allocations_router)
app.include_router(exam_schedules_router)
app.include_router(exam_timetable_router)
app.include_router(timetable_router)
app.include_router(notification_router)
app.include_router(document_router)
app.include_router(reports_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Student Management System"}


if __name__ == "__main__":
    uvicorn.run(
        "student_management:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("APP_ENV", "production") == "development",
    )
