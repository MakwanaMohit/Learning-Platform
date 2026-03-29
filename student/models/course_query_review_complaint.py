from django.db import models
from django.conf import settings


class CourseQuery(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ANSWERED = "answered", "Answered"
        CLOSED = "closed", "Closed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_queries",
        db_index=True,
    )

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="queries",
        db_index=True,
    )

    chapter = models.ForeignKey(
        "course.Chapter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queries",
    )

    question = models.TextField()
    answer = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.course} - {self.student}"

class CourseReview(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
        db_index=True,
    )

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
    )

    rating = models.PositiveSmallIntegerField()
    remark = models.TextField(blank=True)

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_review_per_student_course"
            )
        ]

        indexes = [
            models.Index(fields=["course", "rating"]),
            models.Index(fields=["course", "is_approved"]),
        ]

    def __str__(self):
        return f"{self.course} - {self.rating}"

class Complaint(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        UNDER_REVIEW = "under_review", "Under Review"
        RESOLVED = "resolved", "Resolved"
        REJECTED = "rejected", "Rejected"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaints",
        db_index=True,
    )

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mentor_complaints",
        limit_choices_to={"role": "mentor"},
    )

    subject = models.CharField(max_length=255)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["course"]),
            models.Index(fields=["mentor"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.course and not self.mentor:
            raise ValidationError(
                "Complaint must reference either a course or a mentor."
            )

    def __str__(self):
        return self.subject