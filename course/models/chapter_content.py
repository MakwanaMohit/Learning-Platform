from django.db import models
from learningPlatform.storage import PrivateMediaStorage
import markdown

class ChapterContent(models.Model):

    class ContentType(models.TextChoices):
        VIDEO = "video", "Video"
        MARKDOWN = "markdown", "Markdown"
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Assignment"

    chapter = models.ForeignKey(
        "Chapter",
        on_delete=models.CASCADE,
        related_name="contents",
        db_index=True
    )

    order = models.PositiveIntegerField()

    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        db_index=True
    )

    class Meta:
        ordering = ["order"]
        unique_together = [("chapter", "order")]
        indexes = [
            models.Index(fields=["chapter", "order"]),
            models.Index(fields=["chapter", "content_type"]),
        ]

    def __str__(self):
        return f"{self.chapter.name} - {self.content_type} ({self.order})"

class MarkdownContent(ChapterContent):

    title = models.CharField(max_length=255, blank=True)

    markdown_content = models.TextField()

    rendered_html = models.TextField(
        blank=True,
        editable=False
    )

    # updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Force correct content type
        self.content_type = self.ContentType.MARKDOWN

        # Render markdown
        if self.markdown_content:
            self.rendered_html = markdown.markdown(
                self.markdown_content,
                extensions=[
                    "fenced_code",
                    "codehilite",
                    "tables",
                    "toc",
                ],
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Markdown Block {self.order}"


private_storage = PrivateMediaStorage()

class VideoContent(ChapterContent):

    title = models.CharField(max_length=255)

    video_file = models.FileField(
        upload_to="protected/chapter_videos/",
        storage=private_storage
    )

    def save(self, *args, **kwargs):
        self.content_type = self.ContentType.VIDEO
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
