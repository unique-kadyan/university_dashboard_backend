from contextlib import asynccontextmanager
from fastapi import FastAPI
from uvicorn import uvicorn
from configs.db_config import create_schema, create_tables, engine

# Import controllers
from controllers.authentication_authroziation_controller import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    await create_schema()
    await create_tables()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Student Management System",
    description="API for managing students, courses, exams, and more",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Student Management System"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("student_management:app", host="0.0.0.0", port=8000, reload=True)
