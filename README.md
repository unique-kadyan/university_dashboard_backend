# University Dashboard Backend

A comprehensive Student Management System built with FastAPI, PostgreSQL, and Redis. Provides REST APIs for managing students, faculty, courses, exams, attendance, fees, hostels, library, and more.

## Tech Stack

- **Framework:** FastAPI (async)
- **Database:** PostgreSQL with async SQLAlchemy (asyncpg)
- **Cache:** Redis (token blacklisting, OTP storage)
- **Auth:** JWT (python-jose) with access & refresh tokens
- **Password Hashing:** passlib (bcrypt)
- **Email:** SMTP (Gmail compatible)
- **Validation:** Pydantic v2

## Project Structure

```
StudentManagement/
├── student_management.py          # Application entry point
├── configs/
│   ├── db_config.py               # PostgreSQL async engine & session
│   ├── jwt_config.py              # JWT settings
│   ├── redis_config.py            # Redis connection
│   └── email_config.py            # SMTP settings
├── controllers/                   # API route handlers
├── services/                      # Business logic
├── repositories/                  # Data access layer
├── entities/                      # SQLAlchemy ORM models
├── schemas/                       # Pydantic request/response models
├── dtos/                          # Data transfer objects
├── enums/                         # Python enum definitions
└── utils/
    ├── jwt_handler.py             # Token creation & verification
    ├── token_blacklist.py         # Redis-based token blacklist
    ├── auth_dependency.py         # FastAPI auth dependency
    ├── otp_handler.py             # OTP generation, storage & verification
    └── email_sender.py            # Email sending via SMTP
```

## Architecture

```
Controller → Service → Repository → Database
     ↑                      ↑
  Depends()              Depends(get_db)
```

Database session is injected only at the repository level via FastAPI's dependency injection.

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint           | Description                          | Auth Required |
|--------|--------------------|------------------------------------- |---------------|
| POST   | `/register`        | Register a new user                  | No            |
| POST   | `/login`           | Login and get JWT tokens             | No            |
| POST   | `/logout`          | Revoke access token                  | Yes           |
| POST   | `/refresh`         | Refresh access token                 | Yes (refresh) |
| POST   | `/forgot-password` | Send OTP to email for password reset | No            |
| POST   | `/reset-password`  | Reset password using OTP             | No            |
| POST   | `/verify-email`    | Verify email using OTP               | No            |
| GET    | `/me`              | Get current user info                | Yes           |

### Students Management (`/api/v1/students`)

| Method | Endpoint              | Description                                      | Auth Required |
|--------|-----------------------|--------------------------------------------------|---------------|
| GET    | `/`                   | List all students (paginated, filterable)         | Yes           |
| POST   | `/`                   | Register a new student (creates user + student)   | Yes           |
| GET    | `/search`             | Search students by name, email, ID, admission no. | Yes           |
| GET    | `/export`             | Export students as CSV or Excel                   | Yes (admin/staff) |
| GET    | `/{id}`               | Get student by ID                                 | Yes           |
| PUT    | `/{id}`               | Update student details                            | Yes           |
| DELETE | `/{id}`               | Soft delete student (sets inactive)               | Yes           |
| GET    | `/{id}/profile`       | Get student profile                               | Yes           |
| GET    | `/{id}/enrollments`   | Get student enrollments                           | Yes           |
| GET    | `/{id}/attendance`    | Get student attendance records                    | Yes           |
| GET    | `/{id}/grades`        | Get student grades (via enrollments)              | Yes           |
| GET    | `/{id}/fees`          | Get student fee payments                          | Yes           |
| GET    | `/{id}/documents`     | Get student documents                             | Yes           |
| POST   | `/{id}/upload-photo`  | Upload student profile photo                      | Yes           |

**GET `/` query parameters:**

| Parameter        | Type   | Default | Description                              |
|------------------|--------|---------|------------------------------------------|
| `page`           | int    | 1       | Page number (min 1)                      |
| `page_size`      | int    | 10      | Items per page (1-100)                   |
| `student_status` | string | null    | Filter by status                         |
| `department_id`  | int    | null    | Filter by department                     |
| `program_id`     | int    | null    | Filter by program                        |
| `batch_year`     | int    | null    | Filter by batch year                     |
| `semester`       | int    | null    | Filter by semester                       |
| `category`       | string | null    | Filter by category                       |
| `search`         | string | null    | Search by student ID or admission number |

**GET `/search` query parameters:**

| Parameter | Type   | Default | Description                                          |
|-----------|--------|---------|------------------------------------------------------|
| `q`       | string | —       | Search term (matches name, email, student ID, adm. no.) |
| `limit`   | int    | 20      | Max results (1-100)                                  |

**GET `/export` query parameters:**

| Parameter        | Type   | Default | Description                       |
|------------------|--------|---------|-----------------------------------|
| `format`         | string | csv     | Export format: `csv` or `xlsx`    |
| `student_status` | string | null    | Filter by status                  |
| `batch_year`     | int    | null    | Filter by batch year              |
| `department_id`  | int    | null    | Filter by department              |
| `program_id`     | int    | null    | Filter by program                 |

**POST `/{id}/upload-photo`:**

Accepts a multipart file upload (JPEG, PNG, or WebP, max 5 MB). Updates the user's profile picture.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=student_management
DB_USER=postgres
DB_PASSWORD=your_password
DB_SCHEMA=student_management

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

> For Gmail, use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular password.

### Installation

```bash
pip install fastapi uvicorn sqlalchemy asyncpg psycopg2-binary pydantic[email] python-jose[cryptography] passlib[bcrypt] python-dotenv redis python-multipart openpyxl
```

### Run

```bash
python student_management.py
```

The server starts at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

## Database Modules

| Module         | Entities                                              |
|----------------|-------------------------------------------------------|
| Users          | Users, Admin Staff, Faculty, Students, Parents        |
| Academics      | Universities, Departments, Programs, Courses          |
| Enrollment     | Enrollments, Course Offerings, Program Courses        |
| Scheduling     | Class Schedules, Timetable Slots, Exam Timetables     |
| Assessment     | Assessments, Grades, Semester Results                 |
| Attendance     | Attendance, Attendance Summary                        |
| Finance        | Fee Structures, Fee Payments                          |
| Library        | Library Books, Book Issues                            |
| Hostel         | Hostels, Hostel Rooms, Hostel Allocations             |
| Communication  | Notifications, User Notifications                     |
| Administration | Documents, Audit Logs, System Logs                    |
