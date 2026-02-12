from typing import Optional, Tuple, List

from fastapi import Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.assessments import Assessment
from entities.courses import Course
from entities.course_offerings import ProgramCourse as CourseOffering
from entities.enrollments import Enrollment
from entities.grades import Grades
from entities.semester_results import SemesterResults
from entities.students import Student


class AssessmentGradeRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_assessment_by_id(self, assessment_id: int) -> Assessment | None:
        result = await self.db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        return result.scalar_one_or_none()

    async def find_course_offering_by_id(
        self, offering_id: int
    ) -> CourseOffering | None:
        result = await self.db.execute(
            select(CourseOffering).where(CourseOffering.id == offering_id)
        )
        return result.scalar_one_or_none()

    async def create_assessment(self, assessment: Assessment) -> Assessment:
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def update_assessment(self, assessment: Assessment) -> Assessment:
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def delete_assessment(self, assessment: Assessment) -> None:
        await self.db.delete(assessment)
        await self.db.commit()

    async def find_assessments_paginated(
        self,
        page: int,
        page_size: int,
        course_offering_id: Optional[int] = None,
        assessment_type: Optional[str] = None,
    ) -> Tuple[List[Assessment], int]:
        query = select(Assessment)
        count_query = select(func.count()).select_from(Assessment)

        if course_offering_id:
            query = query.where(Assessment.course_offering_id == course_offering_id)
            count_query = count_query.where(
                Assessment.course_offering_id == course_offering_id
            )

        if assessment_type:
            query = query.where(Assessment.assessment_type == assessment_type)
            count_query = count_query.where(
                Assessment.assessment_type == assessment_type
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Assessment.id.desc()).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        records = list(result.scalars().all())
        return records, total

    async def find_grade_by_id(self, grade_id: int) -> Grades | None:
        result = await self.db.execute(select(Grades).where(Grades.id == grade_id))
        return result.scalar_one_or_none()

    async def find_grade_by_enrollment_assessment(
        self, enrollment_id: int, assessment_id: int
    ) -> Grades | None:
        result = await self.db.execute(
            select(Grades).where(
                and_(
                    Grades.enrollment_id == enrollment_id,
                    Grades.assessment_id == assessment_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_enrollment_by_id(self, enrollment_id: int) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def find_course_by_id(self, course_id: int) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    async def create_grade(self, grade: Grades) -> Grades:
        self.db.add(grade)
        await self.db.commit()
        await self.db.refresh(grade)
        return grade

    async def update_grade(self, grade: Grades) -> Grades:
        await self.db.commit()
        await self.db.refresh(grade)
        return grade

    async def find_grades_paginated(
        self,
        page: int,
        page_size: int,
        enrollment_id: Optional[int] = None,
        course_id: Optional[int] = None,
        assessment_id: Optional[int] = None,
        student_id: Optional[int] = None,
    ) -> Tuple[List[Grades], int]:
        query = select(Grades)
        count_query = select(func.count()).select_from(Grades)

        if enrollment_id:
            query = query.where(Grades.enrollment_id == enrollment_id)
            count_query = count_query.where(Grades.enrollment_id == enrollment_id)

        if course_id:
            query = query.where(Grades.course_id == course_id)
            count_query = count_query.where(Grades.course_id == course_id)

        if assessment_id:
            query = query.where(Grades.assessment_id == assessment_id)
            count_query = count_query.where(Grades.assessment_id == assessment_id)

        if student_id:
            enrollment_subquery = (
                select(Enrollment.id)
                .where(Enrollment.student_id == student_id)
                .scalar_subquery()
            )
            query = query.where(Grades.enrollment_id.in_(enrollment_subquery))
            count_query = count_query.where(
                Grades.enrollment_id.in_(enrollment_subquery)
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Grades.id.desc()).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        records = list(result.scalars().all())
        return records, total

    async def get_student_course_grades_for_semester(
        self, student_id: int, semester: int
    ) -> list:
        """
        For each course in a semester, compute the weighted percentage:
        SUM(marks_obtained / max_marks * weightage)
        """
        query = (
            select(
                Course.id.label("course_id"),
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                Course.credits,
                func.sum(
                    Grades.marks_obtained / Assessment.max_marks * Assessment.weightage
                ).label("weighted_percentage"),
            )
            .join(Assessment, Grades.assessment_id == Assessment.id)
            .join(Course, Grades.course_id == Course.id)
            .join(Enrollment, Grades.enrollment_id == Enrollment.id)
            .join(
                CourseOffering,
                Assessment.course_offering_id == CourseOffering.id,
            )
            .where(
                and_(
                    Enrollment.student_id == student_id,
                    CourseOffering.semester == semester,
                )
            )
            .group_by(Course.id, Course.name, Course.code, Course.credits)
        )

        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_semester_results_for_student(self, student_id: int) -> list:
        query = (
            select(
                SemesterResults.semester,
                SemesterResults.gpa,
                SemesterResults.total_credits_attempted,
            )
            .where(SemesterResults.student_id == student_id)
            .order_by(SemesterResults.semester)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_student_by_id(self, student_id: int) -> Student | None:
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        return result.scalar_one_or_none()

    async def find_students_in_semester(self, semester: int) -> List[Student]:
        result = await self.db.execute(
            select(Student).where(Student.semester == semester)
        )
        return list(result.scalars().all())

    async def find_semester_result(
        self, student_id: int, semester: int
    ) -> SemesterResults | None:
        result = await self.db.execute(
            select(SemesterResults).where(
                and_(
                    SemesterResults.student_id == student_id,
                    SemesterResults.semester == semester,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_semester_result(self, result: SemesterResults) -> SemesterResults:
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def update_semester_result(self, result: SemesterResults) -> SemesterResults:
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def update_student_cgpa(self, student: Student) -> Student:
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def find_enrollment_id_for_student_semester(
        self, student_id: int, semester: int
    ) -> int | None:
        """Find any enrollment_id for a student in the given semester."""
        query = (
            select(Grades.enrollment_id)
            .join(Assessment, Grades.assessment_id == Assessment.id)
            .join(CourseOffering, Assessment.course_offering_id == CourseOffering.id)
            .join(Enrollment, Grades.enrollment_id == Enrollment.id)
            .where(
                and_(
                    Enrollment.student_id == student_id,
                    CourseOffering.semester == semester,
                )
            )
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
