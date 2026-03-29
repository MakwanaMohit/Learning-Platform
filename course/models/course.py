from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


# TODO: add the passing crietirea logic using minimum chapters completed or using progress percentage
# TODO: change the demo video url to video field
# TODO: make one mentor complesery to be part  of the course
# TODO: setup the proper permission setup

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


def validate_video(file):
    valid_extensions = ['.mp4',]
    if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError(f"Only video files are allowed ({', '.join(valid_extensions)}). convert your video to this format first.")


class Course(models.Model):
    LEVEL_CHOICES = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    short_description = models.CharField(max_length=300)
    description = models.TextField()

    thumbnail = models.ImageField(upload_to="public/course_thumbnails/")
    demo_video = models.FileField(
        upload_to="public/course_demo_videos/",
        validators=[validate_video],
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="course"
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="courses_as_mentor",
        limit_choices_to={"role": "mentor"},
    )

    mentors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="mentored_courses",
        blank=True,
        limit_choices_to={"role": "mentor"},
    )

    keywords = models.ManyToManyField(
        "Tag",
        related_name="course",
        blank=True
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="beginner"
    )

    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    duration_hours = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("course:course_detail", kwargs={"course_slug": self.slug})

    def __str__(self):
        return self.title
