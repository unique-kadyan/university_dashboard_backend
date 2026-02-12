from contextlib import asynccontextmanager
from fastapi import FastAPI
from uvicorn import uvicorn
from configs.db_config import create_schema, create_tables, engine

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


@app.get("/")
async def root():
    return {"message": "Welcome to Student Management System"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("student_management:app", host="0.0.0.0", port=8000, reload=True)
