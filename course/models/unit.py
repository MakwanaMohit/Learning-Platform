from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Unit(models.Model):

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name="units",
        db_index=True
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        blank=True
    )

    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    duration = models.DurationField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_unit_order_per_course"
            ),
            models.UniqueConstraint(
                fields=["course", "slug"],
                name="unique_unit_slug_per_course"
            ),
        ]

        indexes = [
            models.Index(fields=["course", "order"]),
            models.Index(fields=["course", "slug"]),
        ]

    def get_absolute_url(self):
        return reverse("course:unit_chapter_list", kwargs={"course_slug": self.course.slug,"unit_slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Unit.objects.filter(
                course=self.course,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
