from student.models import Enrollment
from course.models import Course, Unit, Chapter
from accounts.models import User

def is_course_owner(user: User, course: Course) -> bool:
    if not user.is_authenticated or user.role != 'mentor':
        return False

    return (
        user == course.mentor or
        course.mentors.filter(id=user.id).exists()
    )

def is_enrolled(user: User, course: Course) -> bool:
    if not user.is_authenticated:
        return False

    return Enrollment.objects.filter(
        course_id=course.id,
        student_id=user.id
    ).exists()


def is_course_published(course: Course) -> bool:
    return course.status == 'published'


def _base_access(user: User, course: Course, *, is_locked=False, is_preview=False) -> bool:
    if is_course_owner(user, course):
        return True

    if not is_course_published(course):
        return False
    if is_locked:
        return False

    if is_preview:
        return True

    return is_enrolled(user, course)


def can_access_course(user: User, course: Course) -> bool:
    return _base_access(
        user=user,
        course=course,
        is_locked=False,
        is_preview=True
    )


def can_access_unit(user: User, unit: Unit) -> bool:
    return _base_access(
        user=user,
        course=unit.course,
        is_locked=unit.is_locked,
        is_preview=False
    )


def can_access_chapter(user: User, chapter: Chapter) -> bool:
    unit = chapter.unit

    return _base_access(
        user=user,
        course=unit.course,
        is_locked=(unit.is_locked or chapter.is_locked),
        is_preview=chapter.is_preview
    )
