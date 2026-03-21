from django.db import models
from django.urls import reverse


class Chapter(models.Model):

    unit = models.ForeignKey(
        "Unit",
        on_delete=models.CASCADE,
        related_name="chapters",
        db_index=True
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        db_index=True
    )

    description = models.TextField(blank=True)

    order = models.PositiveIntegerField()

    duration = models.DurationField(null=True, blank=True)

    # Learning Logic
    is_compulsory = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_preview = models.BooleanField(default=False)

    # Self prerequisite relationship
    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="required_for"
    )

    # Publishing control
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        unique_together = [
            ("unit", "order"),
            ("unit", "slug"),
        ]
        indexes = [
            models.Index(fields=["unit", "order"]),
            models.Index(fields=["unit", "slug"]),
            models.Index(fields=["is_published"]),
        ]

    def __str__(self):
        return f"{self.unit.title} - {self.name}"

    def get_absolute_url(self):
        return reverse(
            "chapter_detail",
            kwargs={
                "course_slug": self.unit.course.slug,
                "unit_order": self.unit.order,
                "chapter_slug": self.slug,
            },
        )