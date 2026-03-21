from django.db import models
from django.conf import settings
class Wishlist(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        db_index=True
    )

    course = models.ForeignKey(
        'course.Course',
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
        db_index=True
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_wishlist_per_student"
            )
        ]

        indexes = [
            models.Index(fields=["student", "added_at"]),
        ]