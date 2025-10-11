"""リポジトリパッケージ"""

from .course_repository import CourseRepository
from .student_repository import StudentRepository
from .grade_repository import GradeRepository

__all__ = ['CourseRepository', 'StudentRepository', 'GradeRepository']
