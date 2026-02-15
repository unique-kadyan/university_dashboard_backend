# University Dashboard Backend

A comprehensive Student Management System built with FastAPI, PostgreSQL, and Redis. Provides REST APIs for managing students, faculty, departments, programs, courses, enrollments, attendance, assessments, grades, fees, hostels, library, and more.

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
│   ├── authentication_authroziation_controller.py
│   ├── students_management_controller.py
│   ├── faculty_management_controller.py
│   ├── department_management_controller.py
│   ├── programs_courses_controller.py
│   ├── enrollment_management_controller.py
│   ├── attendance_management_controller.py
│   ├── assessments_grades_controller.py
│   ├── fees_management_controller.py
│   ├── library_management_controllers.py
│   ├── hostel_management_controller.py
│   ├── examination_management_controller.py
│   ├── timetable_management.py
│   ├── notification_management_controller.py
│   ├── document_management_controller.py
│   └── reports_analytics_controller.py
├── services/                      # Business logic
│   ├── auth_service.py
│   ├── student_service.py
│   ├── faculty_service.py
│   ├── department_service.py
│   ├── program_course_service.py
│   ├── enrollment_service.py
│   ├── attendance_service.py
│   ├── assessment_grade_service.py
│   ├── fee_service.py
│   ├── library_service.py
│   ├── hostel_service.py
│   ├── exam_service.py
│   ├── timetable_service.py
│   ├── notification_service.py
│   ├── document_service.py
│   └── report_service.py
├── repositories/                  # Data access layer
│   ├── user_repository.py
│   ├── student_repository.py
│   ├── faculty_repository.py
│   ├── department_repository.py
│   ├── program_course_repository.py
│   ├── enrollment_repository.py
│   ├── attendance_repository.py
│   ├── assessment_grade_repository.py
│   ├── fee_repository.py
│   ├── library_repository.py
│   ├── hostel_repository.py
│   ├── exam_repository.py
│   ├── timetable_repository.py
│   ├── notification_repository.py
│   ├── document_repository.py
│   └── report_repository.py
├── entities/                      # SQLAlchemy ORM models
├── schemas/                       # Pydantic request/response models
├── dtos/                          # Data transfer objects
├── enums/                         # Python enum definitions
└── utils/
    ├── jwt_handler.py             # Token creation & verification
    ├── token_blacklist.py         # Redis-based token blacklist
    ├── auth_dependency.py         # FastAPI auth dependency
    ├── otp_handler.py             # OTP generation, storage & verification
    ├── email_sender.py            # Email sending via SMTP
    └── safe_update.py             # Protected-field-aware entity updater
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

### Students (`/api/v1/students`)

| Method | Endpoint              | Description                                      | Auth Required     |
|--------|-----------------------|--------------------------------------------------|-------------------|
| GET    | `/`                   | List all students (paginated, filterable)         | Yes               |
| POST   | `/`                   | Register a new student (creates user + student)   | Yes               |
| GET    | `/search`             | Search students by name, email, ID, admission no. | Yes              |
| GET    | `/export`             | Export students as CSV or Excel                   | Yes (admin/staff) |
| GET    | `/{id}`               | Get student by ID                                 | Yes               |
| PUT    | `/{id}`               | Update student details                            | Yes               |
| DELETE | `/{id}`               | Soft delete student (sets inactive)               | Yes               |
| GET    | `/{id}/enrollments`   | Get student enrollments                           | Yes               |
| GET    | `/{id}/attendance`    | Get student attendance records                    | Yes               |
| GET    | `/{id}/grades`        | Get student grades                                | Yes               |
| GET    | `/{id}/fees`          | Get student fee payments                          | Yes               |
| GET    | `/{id}/documents`     | Get student documents                             | Yes               |
| POST   | `/{id}/upload-photo`  | Upload student profile photo                      | Yes               |

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

| Parameter | Type   | Default | Description                                             |
|-----------|--------|---------|---------------------------------------------------------|
| `q`       | string | —       | Search term (matches name, email, student ID, adm. no.) |
| `limit`   | int    | 20      | Max results (1-100)                                     |

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

### Faculty (`/api/v1/faculty`)

| Method | Endpoint              | Description                           | Auth Required          |
|--------|-----------------------|---------------------------------------|------------------------|
| GET    | `/`                   | List all faculty (paginated)          | Yes                    |
| POST   | `/`                   | Register a new faculty member         | Yes (admin/staff)      |
| GET    | `/{id}`               | Get faculty by ID                     | Yes                    |
| PUT    | `/{id}`               | Update faculty details                | Yes (admin/staff)      |
| DELETE | `/{id}`               | Delete faculty                        | Yes (admin/staff)      |
| GET    | `/{id}/courses`       | Get courses taught by faculty         | Yes                    |
| GET    | `/{id}/schedule`      | Get faculty class schedule            | Yes                    |
| GET    | `/{id}/students`      | Get students under faculty            | Yes                    |
| POST   | `/{id}/upload-photo`  | Upload faculty profile photo          | Yes (admin/staff/self) |

**GET `/` query parameters:**

| Parameter         | Type   | Default | Description                                                  |
|-------------------|--------|---------|--------------------------------------------------------------|
| `page`            | int    | 1       | Page number (min 1)                                          |
| `page_size`       | int    | 10      | Items per page (1-100)                                       |
| `faculty_status`  | string | null    | Filter by status (active, inactive, suspended, retired, terminated) |
| `department_id`   | int    | null    | Filter by department ID                                      |
| `employment_type` | string | null    | Filter by type (permanent, contract, visiting, parttime)     |
| `is_hod`          | bool   | null    | Filter by HOD status                                         |
| `search`          | string | null    | Search by employee ID or designation                         |

### Departments (`/api/v1/departments`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List all departments (paginated)      | Yes               |
| POST   | `/`                   | Create a new department               | Yes (admin/staff) |
| GET    | `/{id}`               | Get department by ID                  | Yes               |
| PUT    | `/{id}`               | Update department details             | Yes (admin/staff) |
| DELETE | `/{id}`               | Delete department                     | Yes (admin/staff) |
| GET    | `/{id}/faculty`       | Get faculty in the department         | Yes               |
| GET    | `/{id}/students`      | Get students in the department        | Yes               |
| GET    | `/{id}/courses`       | Get courses offered by department     | Yes               |

**GET `/` query parameters:**

| Parameter   | Type   | Default | Description                |
|-------------|--------|---------|----------------------------|
| `page`      | int    | 1       | Page number (min 1)        |
| `page_size` | int    | 10      | Items per page (1-100)     |
| `is_active` | bool   | null    | Filter by active status    |
| `search`    | string | null    | Search by name or code     |

### Programs (`/api/v1/programs`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List all programs (paginated)         | Yes               |
| POST   | `/`                   | Create a new program                  | Yes (admin/staff) |
| GET    | `/{id}`               | Get program by ID                     | Yes               |
| PUT    | `/{id}`               | Update program details                | Yes (admin/staff) |
| DELETE | `/{id}`               | Delete program                        | Yes (admin/staff) |
| GET    | `/{id}/courses`       | Get courses in the program            | Yes               |

**GET `/` query parameters:**

| Parameter     | Type   | Default | Description                |
|---------------|--------|---------|----------------------------|
| `page`        | int    | 1       | Page number (min 1)        |
| `page_size`   | int    | 10      | Items per page (1-100)     |
| `department_id` | int  | null    | Filter by department       |
| `degree_type` | string | null    | Filter by degree type      |
| `is_active`   | bool   | null    | Filter by active status    |
| `search`      | string | null    | Search by name or code     |

### Courses (`/api/v1/courses`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List all courses (paginated)          | Yes               |
| POST   | `/`                   | Create a new course                   | Yes (admin/staff) |
| GET    | `/{id}`               | Get course by ID                      | Yes               |
| PUT    | `/{id}`               | Update course details                 | Yes (admin/staff) |
| DELETE | `/{id}`               | Delete course                         | Yes (admin/staff) |
| GET    | `/{id}/prerequisites` | Get course prerequisites              | Yes               |

**GET `/` query parameters:**

| Parameter     | Type   | Default | Description                |
|---------------|--------|---------|----------------------------|
| `page`        | int    | 1       | Page number (min 1)        |
| `page_size`   | int    | 10      | Items per page (1-100)     |
| `department_id` | int  | null    | Filter by department       |
| `course_type` | string | null    | Filter by course type      |
| `level`       | string | null    | Filter by level            |
| `is_active`   | bool   | null    | Filter by active status    |
| `search`      | string | null    | Search by name or code     |

### Course Offerings (`/api/v1/course-offerings`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List all course offerings (paginated) | Yes               |
| POST   | `/`                   | Create a new course offering          | Yes (admin/staff) |
| GET    | `/{id}`               | Get offering by ID                    | Yes               |
| PUT    | `/{id}`               | Update offering details               | Yes (admin/staff) |
| DELETE | `/{id}`               | Delete offering                       | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter        | Type   | Default | Description                |
|------------------|--------|---------|----------------------------|
| `page`           | int    | 1       | Page number (min 1)        |
| `page_size`      | int    | 10      | Items per page (1-100)     |
| `program_id`     | int    | null    | Filter by program          |
| `course_id`      | int    | null    | Filter by course           |
| `semester`       | int    | null    | Filter by semester         |
| `acedemic_year`  | string | null    | Filter by academic year    |
| `offering_status`| string | null    | Filter by status           |

### Enrollments (`/api/v1/enrollments`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/verify-eligibility` | Check student eligibility for program | Yes               |
| GET    | `/`                   | List all enrollments (paginated)      | Yes               |
| POST   | `/`                   | Create a new enrollment               | Yes (admin/staff) |
| POST   | `/bulk`               | Bulk enroll multiple students         | Yes (admin/staff) |
| GET    | `/{id}`               | Get enrollment by ID                  | Yes               |
| PUT    | `/{id}`               | Update enrollment                     | Yes (admin/staff) |
| DELETE | `/{id}`               | Drop enrollment                       | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter           | Type   | Default | Description                |
|---------------------|--------|---------|----------------------------|
| `page`              | int    | 1       | Page number (min 1)        |
| `page_size`         | int    | 10      | Items per page (1-100)     |
| `student_id`        | int    | null    | Filter by student          |
| `program_id`        | int    | null    | Filter by program          |
| `enrollment_status` | string | null    | Filter by status           |

### Attendance (`/api/v1/attendance`)

| Method | Endpoint              | Description                             | Auth Required             |
|--------|-----------------------|-----------------------------------------|---------------------------|
| GET    | `/summary`            | Get attendance summary                  | Yes                       |
| GET    | `/reports`            | Get attendance reports (aggregated)     | Yes                       |
| GET    | `/defaulters`         | Get students below attendance threshold | Yes                       |
| GET    | `/`                   | List attendance records (paginated)     | Yes                       |
| POST   | `/`                   | Mark attendance                         | Yes (admin/staff/faculty) |
| POST   | `/bulk`               | Bulk mark attendance                    | Yes (admin/staff/faculty) |
| PUT    | `/{id}`               | Update attendance record                | Yes (admin/staff/faculty) |

**GET `/` query parameters:**

| Parameter           | Type     | Default | Description                |
|---------------------|----------|---------|----------------------------|
| `page`              | int      | 1       | Page number (min 1)        |
| `page_size`         | int      | 10      | Items per page (1-100)     |
| `enrollment_id`     | int      | null    | Filter by enrollment       |
| `student_id`        | int      | null    | Filter by student          |
| `attendance_status` | string   | null    | Filter by status           |
| `date_from`         | datetime | null    | Start date filter          |
| `date_to`           | datetime | null    | End date filter            |

**GET `/defaulters` query parameters:**

| Parameter   | Type  | Default | Description                    |
|-------------|-------|---------|--------------------------------|
| `threshold` | float | 75.0    | Attendance percentage threshold|

### Assessments (`/api/v1/assessments`)

| Method | Endpoint              | Description                           | Auth Required             |
|--------|-----------------------|---------------------------------------|---------------------------|
| GET    | `/`                   | List all assessments (paginated)      | Yes                       |
| POST   | `/`                   | Create a new assessment               | Yes (admin/staff/faculty) |
| GET    | `/{id}`               | Get assessment by ID                  | Yes                       |
| PUT    | `/{id}`               | Update assessment                     | Yes (admin/staff/faculty) |
| DELETE | `/{id}`               | Delete assessment                     | Yes (admin/staff)         |

**GET `/` query parameters:**

| Parameter            | Type   | Default | Description                  |
|----------------------|--------|---------|------------------------------|
| `page`               | int    | 1       | Page number (min 1)          |
| `page_size`          | int    | 10      | Items per page (1-100)       |
| `course_offering_id` | int    | null    | Filter by course offering    |
| `assessment_type`    | string | null    | Filter by assessment type    |

### Grades (`/api/v1/grades`)

| Method | Endpoint              | Description                           | Auth Required             |
|--------|-----------------------|---------------------------------------|---------------------------|
| GET    | `/calculate-sgpa`     | Calculate SGPA for a student/semester | Yes                       |
| GET    | `/calculate-cgpa`     | Calculate CGPA for a student          | Yes                       |
| GET    | `/`                   | List all grades (paginated)           | Yes                       |
| POST   | `/`                   | Submit a grade                        | Yes (admin/staff/faculty) |
| PUT    | `/{id}`               | Update a grade                        | Yes (admin/staff/faculty) |
| POST   | `/bulk`               | Bulk submit grades                    | Yes (admin/staff/faculty) |
| POST   | `/publish`            | Publish semester results              | Yes (admin/staff)         |

**GET `/` query parameters:**

| Parameter       | Type | Default | Description              |
|-----------------|------|---------|--------------------------|
| `page`          | int  | 1       | Page number (min 1)      |
| `page_size`     | int  | 10      | Items per page (1-100)   |
| `enrollment_id` | int  | null    | Filter by enrollment     |
| `course_id`     | int  | null    | Filter by course         |
| `assessment_id` | int  | null    | Filter by assessment     |
| `student_id`    | int  | null    | Filter by student        |

**GET `/calculate-sgpa` query parameters:**

| Parameter    | Type | Description          |
|--------------|------|----------------------|
| `student_id` | int  | Student ID (required)|
| `semester`   | int  | Semester (required)  |

**GET `/calculate-cgpa` query parameters:**

| Parameter    | Type | Description          |
|--------------|------|----------------------|
| `student_id` | int  | Student ID (required)|

### Fee Structures (`/api/v1/fee-structures`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List fee structures (paginated)       | Yes               |
| POST   | `/`                   | Create a new fee structure            | Yes (admin/staff) |
| GET    | `/{id}`               | Get fee structure by ID               | Yes               |
| PUT    | `/{id}`               | Update fee structure                  | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `page`          | int    | 1       | Page number (min 1)        |
| `page_size`     | int    | 10      | Items per page (1-100)     |
| `program_id`    | int    | null    | Filter by program          |
| `student_id`    | int    | null    | Filter by student          |
| `acedamic_year` | string | null    | Filter by academic year    |
| `semester`      | int    | null    | Filter by semester         |

### Fee Payments (`/api/v1/fee-payments`)

| Method | Endpoint              | Description                             | Auth Required     |
|--------|-----------------------|-----------------------------------------|-------------------|
| GET    | `/pending`            | Get pending (unpaid/partial) payments   | Yes               |
| GET    | `/defaulters`         | Get students with overdue fees          | Yes (admin/staff) |
| GET    | `/`                   | List all payments (paginated)           | Yes               |
| POST   | `/`                   | Record a fee payment                    | Yes (admin/staff) |
| POST   | `/refund`             | Process a payment refund                | Yes (admin/staff) |
| GET    | `/{id}`               | Get payment details                     | Yes               |
| GET    | `/{id}/receipt`       | Generate payment receipt                | Yes               |

**GET `/` query parameters:**

| Parameter          | Type   | Default | Description                |
|--------------------|--------|---------|----------------------------|
| `page`             | int    | 1       | Page number (min 1)        |
| `page_size`        | int    | 10      | Items per page (1-100)     |
| `student_id`       | int    | null    | Filter by student          |
| `fee_structure_id` | int    | null    | Filter by fee structure    |
| `payment_status`   | string | null    | Filter by status           |

### Library (`/api/v1/library`)

**Books:**

| Method | Endpoint              | Description                        | Auth Required     |
|--------|-----------------------|------------------------------------|-------------------|
| GET    | `/books/search`       | Search books by title, author, ISBN | Yes              |
| GET    | `/books`              | List all books (paginated)         | Yes               |
| POST   | `/books`              | Add a new book                     | Yes (admin/staff) |
| GET    | `/books/{id}`         | Get book details                   | Yes               |
| PUT    | `/books/{id}`         | Update book                        | Yes (admin/staff) |
| DELETE | `/books/{id}`         | Delete book                        | Yes (admin/staff) |

**GET `/books` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `page`          | int    | 1       | Page number (min 1)        |
| `page_size`     | int    | 10      | Items per page (1-100)     |
| `category`      | string | null    | Filter by category         |
| `department_id` | int    | null    | Filter by department       |
| `is_referenced` | bool   | null    | Filter reference books     |

**Circulation:**

| Method | Endpoint              | Description                        | Auth Required     |
|--------|-----------------------|------------------------------------|-------------------|
| GET    | `/issued`             | Get currently issued books         | Yes               |
| GET    | `/overdue`            | Get overdue books with days count  | Yes               |
| POST   | `/issue`              | Issue a book to a user             | Yes (admin/staff) |
| PUT    | `/return`             | Return an issued book              | Yes               |
| POST   | `/renew`              | Renew (extend due date)            | Yes               |
| POST   | `/pay-fine`           | Pay fine for overdue book          | Yes               |

### Hostels (`/api/v1/hostels`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List all hostels (paginated)          | Yes               |
| POST   | `/`                   | Create a new hostel                   | Yes (admin/staff) |
| GET    | `/{id}`               | Get hostel by ID                      | Yes               |
| PUT    | `/{id}`               | Update hostel details                 | Yes (admin/staff) |
| GET    | `/{id}/rooms`         | Get all rooms in a hostel             | Yes               |

**GET `/` query parameters:**

| Parameter     | Type   | Default | Description                |
|---------------|--------|---------|----------------------------|
| `page`        | int    | 1       | Page number (min 1)        |
| `page_size`   | int    | 10      | Items per page (1-100)     |
| `hostel_type` | string | null    | Filter by hostel type      |
| `is_active`   | bool   | null    | Filter by active status    |

### Hostel Rooms (`/api/v1/hostel-rooms`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/available`          | Get available rooms                   | Yes               |
| GET    | `/`                   | List all rooms (paginated)            | Yes               |
| POST   | `/`                   | Add a new room to a hostel            | Yes (admin/staff) |
| GET    | `/{id}`               | Get room by ID                        | Yes               |
| PUT    | `/{id}`               | Update room details                   | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter     | Type   | Default | Description                |
|---------------|--------|---------|----------------------------|
| `page`        | int    | 1       | Page number (min 1)        |
| `page_size`   | int    | 10      | Items per page (1-100)     |
| `hostel_id`   | int    | null    | Filter by hostel           |
| `room_type`   | string | null    | Filter by room type        |
| `room_status` | string | null    | Filter by status           |
| `is_active`   | bool   | null    | Filter by active status    |

### Hostel Allocations (`/api/v1/hostel-allocations`)

| Method | Endpoint                  | Description                             | Auth Required     |
|--------|---------------------------|-----------------------------------------|-------------------|
| GET    | `/history/{student_id}`   | Get student's full allocation history   | Yes               |
| GET    | `/`                       | List all allocations (paginated)        | Yes               |
| POST   | `/`                       | Allocate a room to a student            | Yes (admin/staff) |
| PUT    | `/{id}`                   | Update/transfer allocation              | Yes (admin/staff) |
| DELETE | `/{id}`                   | Vacate room (keeps history record)      | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter           | Type   | Default | Description                |
|---------------------|--------|---------|----------------------------|
| `page`              | int    | 1       | Page number (min 1)        |
| `page_size`         | int    | 10      | Items per page (1-100)     |
| `student_id`        | int    | null    | Filter by student          |
| `hostel_id`         | int    | null    | Filter by hostel           |
| `room_id`           | int    | null    | Filter by room             |
| `allocation_status` | string | null    | Filter by status           |
| `acedamic_year`     | string | null    | Filter by academic year    |

**Allocation history:** Each allocation (active, vacated, transferred) is preserved as a separate record. The `DELETE /{id}` endpoint marks the allocation as `VACATED` rather than deleting it. Room transfers create a `TRANSFERRED` record for the old allocation and a new `ACTIVE` record for the new room. Use `GET /history/{student_id}` to retrieve a student's complete hostel allocation timeline.

### Exam Schedules (`/api/v1/exams`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/`                   | List exam schedules (paginated)       | Yes               |
| POST   | `/`                   | Create a new exam schedule            | Yes (admin/staff) |
| GET    | `/{id}`               | Get exam schedule by ID               | Yes               |
| PUT    | `/{id}`               | Update exam schedule                  | Yes (admin/staff) |
| DELETE | `/{id}`               | Delete exam schedule                  | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `page`          | int    | 1       | Page number (min 1)        |
| `page_size`     | int    | 10      | Items per page (1-100)     |
| `course_id`     | int    | null    | Filter by course           |
| `academic_year` | string | null    | Filter by academic year    |
| `semester`      | int    | null    | Filter by semester         |
| `status`        | string | null    | Filter by status           |
| `exam_type`     | string | null    | Filter by exam type        |

**Exam status values:** `draft`, `scheduled`, `ongoing`, `completed`, `cancelled`

**Exam type values:** `midterm`, `final`, `supplementary`, `improvement`

### Exam Timetable (`/api/v1/exam-timetable`)

| Method | Endpoint              | Description                              | Auth Required     |
|--------|-----------------------|------------------------------------------|-------------------|
| GET    | `/export`             | Export timetable data (with filters)     | Yes               |
| GET    | `/student/{id}`       | Get a student's exam schedule            | Yes               |
| GET    | `/`                   | List timetable entries (paginated)       | Yes               |
| POST   | `/`                   | Create a new timetable entry             | Yes (admin/staff) |
| PUT    | `/{id}`               | Update a timetable entry                 | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter           | Type | Default | Description                |
|---------------------|------|---------|----------------------------|
| `page`              | int  | 1       | Page number (min 1)        |
| `page_size`         | int  | 10      | Items per page (1-100)     |
| `exam_schedule_id`  | int  | null    | Filter by exam schedule    |
| `course_offering_id`| int  | null    | Filter by course offering  |

**GET `/export` query parameters:**

| Parameter          | Type   | Default | Description                |
|--------------------|--------|---------|----------------------------|
| `exam_schedule_id` | int    | null    | Filter by exam schedule    |
| `academic_year`    | string | null    | Filter by academic year    |
| `semester`         | int    | null    | Filter by semester         |

**Student exam schedule:** The `GET /student/{id}` endpoint returns all exam timetable entries for a student based on the programs they are enrolled in. Each entry includes the exam name, type, date, time, venue, duration, and max marks.

### Timetable (`/api/v1/timetable`)

| Method | Endpoint              | Description                                | Auth Required     |
|--------|-----------------------|--------------------------------------------|-------------------|
| POST   | `/generate`           | Generate class schedules (bulk)            | Yes (admin/staff) |
| GET    | `/student/{id}`       | Get a student's weekly timetable           | Yes               |
| GET    | `/faculty/{id}`       | Get a faculty member's weekly timetable    | Yes               |
| GET    | `/room/{number}`      | Get a room's weekly timetable              | Yes               |
| GET    | `/`                   | List all class schedules (paginated)       | Yes               |
| PUT    | `/{id}`               | Update a class schedule                    | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter            | Type   | Default | Description                |
|----------------------|--------|---------|----------------------------|
| `page`               | int    | 1       | Page number (min 1)        |
| `page_size`          | int    | 10      | Items per page (1-100)     |
| `course_offering_id` | int    | null    | Filter by course offering  |
| `slot_id`            | int    | null    | Filter by timetable slot   |
| `room_no`            | string | null    | Filter by room number      |
| `is_active`          | bool   | null    | Filter by active status    |

**POST `/generate`:** Accepts a list of `{course_offering_id, slot_id, room_no}` items. Validates that each course offering and slot exist, checks for room-slot conflicts, and bulk creates class schedules.

**Student/Faculty/Room timetable:** Returns the weekly schedule grouped by entries, each containing course name, code, day of week, start/end time, room number, and slot type.

### Notifications (`/api/v1/notifications`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/unread`             | Get unread notification count         | Yes               |
| POST   | `/`                   | Send a new notification               | Yes (admin/staff) |
| GET    | `/`                   | List notifications for current user   | Yes               |
| GET    | `/{id}`               | Get notification details              | Yes               |
| PUT    | `/{id}/read`          | Mark a notification as read           | Yes               |
| DELETE | `/{id}`               | Delete a notification                 | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter | Type | Default | Description            |
|-----------|------|---------|------------------------|
| `page`    | int  | 1       | Page number (min 1)    |
| `page_size` | int | 10    | Items per page (1-100) |

**POST `/`:** Creates a notification and fans out `UserNotification` records based on `target_audience`. Supported audiences: `all`, `students`, `faculty`, `staff`, `specific` (requires `target_id` list).

### Documents (`/api/v1/documents`)

| Method | Endpoint              | Description                           | Auth Required     |
|--------|-----------------------|---------------------------------------|-------------------|
| GET    | `/search`             | Search documents by title/description | Yes               |
| POST   | `/upload`             | Upload a new document                 | Yes               |
| GET    | `/`                   | List all documents (paginated)        | Yes               |
| GET    | `/{id}`               | Get document metadata                 | Yes               |
| GET    | `/{id}/download`      | Download document file                | Yes               |
| DELETE | `/{id}`               | Delete a document                     | Yes (admin/staff) |

**GET `/` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `page`          | int    | 1       | Page number (min 1)        |
| `page_size`     | int    | 10      | Items per page (1-100)     |
| `user_id`       | int    | null    | Filter by uploader         |
| `document_type` | string | null    | Filter by document type    |

**GET `/search` query parameters:**

| Parameter | Type   | Default | Description                          |
|-----------|--------|---------|--------------------------------------|
| `q`       | string | —       | Search term (matches title, description, file name) |
| `limit`   | int    | 20      | Max results (1-100)                  |

**POST `/upload`:** Accepts a multipart form with `file` (required), `title`, `description`, `document_type`, `related_entity_type`, `related_entity_id`, `is_public`, `tags`. Allowed file types: PDF, JPEG, PNG, WebP, DOC, DOCX, XLS, XLSX, TXT, CSV. Max file size: 10 MB.

### Reports (`/api/v1/reports`)

| Method | Endpoint              | Description                              | Auth Required     |
|--------|-----------------------|------------------------------------------|-------------------|
| GET    | `/student-performance`| Student performance summary              | Yes (admin/staff) |
| GET    | `/attendance`         | Attendance statistics                    | Yes (admin/staff) |
| GET    | `/fee-collection`     | Fee collection summary                   | Yes (admin/staff) |
| GET    | `/exam-results`       | Exam results statistics                  | Yes (admin/staff) |
| GET    | `/library-stats`      | Library usage statistics                 | Yes (admin/staff) |
| GET    | `/hostel-occupancy`   | Hostel occupancy report                  | Yes (admin/staff) |
| GET    | `/department-wise`    | Department-wise statistics               | Yes (admin/staff) |

**GET `/student-performance` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `department_id` | int    | null    | Filter by department       |
| `program_id`    | int    | null    | Filter by program          |
| `academic_year` | string | null    | Filter by academic year    |

**GET `/attendance` query parameters:**

| Parameter            | Type | Default | Description                |
|----------------------|------|---------|----------------------------|
| `department_id`      | int  | null    | Filter by department       |
| `course_offering_id` | int  | null    | Filter by course offering  |

**GET `/fee-collection` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `academic_year` | string | null    | Filter by academic year    |
| `semester`      | int    | null    | Filter by semester         |
| `department_id` | int    | null    | Filter by department       |

**GET `/exam-results` query parameters:**

| Parameter       | Type   | Default | Description                |
|-----------------|--------|---------|----------------------------|
| `academic_year` | string | null    | Filter by academic year    |
| `semester`      | int    | null    | Filter by semester         |

### Analytics (`/api/v1/analytics`)

| Method | Endpoint              | Description                              | Auth Required     |
|--------|-----------------------|------------------------------------------|-------------------|
| GET    | `/dashboard`          | Dashboard summary statistics             | Yes (admin/staff) |
| GET    | `/trends`             | Enrollment, fee, and attendance trends   | Yes (admin/staff) |

**GET `/trends` query parameters:**

| Parameter | Type | Default | Description                    |
|-----------|------|---------|--------------------------------|
| `months`  | int  | 12      | Number of months to analyze (1-60) |

**Dashboard:** Returns total counts for students, faculty, departments, programs, courses, active enrollments, total fees collected, library books, and hostel occupancy percentage.

**Trends:** Returns monthly time-series data for enrollment counts, fee collection amounts, and attendance counts over the specified period.

## Role-Based Access

| Role    | Permissions                                                              |
|---------|--------------------------------------------------------------------------|
| admin   | Full access to all endpoints                                             |
| staff   | Full access to all endpoints                                             |
| faculty | Read access + create/update attendance, assessments, and grades          |
| student | Read-only access to own data (enrollments, attendance, grades, fees)     |

## Security

### Authentication & Tokens

- **JWT** with separate access (30 min) and refresh (7 day) tokens
- JWT secret key is **required** via environment variable (no fallback default)
- Logout blacklists **both** access and refresh tokens via Redis
- Refresh token type is validated before issuing new tokens

### Password & OTP

- Minimum **8 characters** enforced on all password fields (register, login, reset)
- Usernames require **3–50 characters**
- Passwords hashed with **bcrypt** (passlib)
- OTPs generated with `secrets` (cryptographically secure RNG)
- OTP verification rate-limited to **5 attempts** per email, tracked in Redis

### API Security

- **CORS** middleware with configurable allowed origins (`CORS_ORIGINS` env var)
- Security headers on every response: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`
- Generic error messages on login/registration to prevent **user enumeration**
- Reload mode disabled by default; only enabled when `APP_ENV=development`

### File Uploads

- **Dual validation**: MIME type allowlist + file extension allowlist
- **Chunked size check**: file read in 1 MB chunks, rejected immediately if over 10 MB (documents) or 5 MB (photos)
- Allowed document types: PDF, JPEG, PNG, WebP, DOC, DOCX, XLS, XLSX, TXT, CSV
- Allowed photo extensions: `.jpg`, `.jpeg`, `.png`, `.webp`
- File paths **not exposed** in API responses

### Data Access

- Document download/view enforces **ownership checks** (owner, public, or admin/staff)
- Update operations filter out **protected fields** (`id`, `created_at`, `created_by`) via `apply_update()` utility
- CSV/Excel exports **sanitize cell values** to prevent formula injection
- Foreign keys configured with `ondelete` policies (CASCADE, SET NULL, or RESTRICT) to maintain referential integrity
- SQL injection prevented: ORM parameterized queries + schema name validation with regex

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

# JWT (REQUIRED — app will not start without JWT_SECRET_KEY)
JWT_SECRET_KEY=generate-a-strong-random-secret-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:3000
```

> `JWT_SECRET_KEY` is **required** — the app raises a `RuntimeError` on startup if it is not set. Generate one with: `python -c "import secrets; print(secrets.token_urlsafe(64))"`

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
| Scheduling     | Class Schedules, Timetable Slots                       |
| Examination    | Exam Schedules, Exam Timetables                        |
| Assessment     | Assessments, Grades, Semester Results                 |
| Attendance     | Attendance, Attendance Summary                        |
| Finance        | Fee Structures, Fee Payments                          |
| Library        | Library Books, Book Issues                            |
| Hostel         | Hostels, Hostel Rooms, Hostel Allocations             |
| Communication  | Notifications, User Notifications                     |
| Administration | Documents, Audit Logs, System Logs                     |
