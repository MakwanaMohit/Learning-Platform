from django.db import models
from django.conf import settings


class Enrollment(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        db_index=True,
    )

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
        db_index=True,
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_enrollment"
            )
        ]

        indexes = [
            models.Index(fields=["student", "course"]),
            models.Index(fields=["course", "completed"]),
            models.Index(fields=["student", "completed"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.course}"