from django.db import models

from course.models import ChapterContent


class Quiz(ChapterContent):

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_questions = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.content_type = self.ContentType.QUIZ
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Question(models.Model):

    class QuestionType(models.TextChoices):
        MCQ = "mcq", "Single Choice"
        MSQ = "msq", "Multiple Choice"
        NUMERIC = "numeric", "Numeric"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    title = models.TextField()

    image = models.ImageField(
        upload_to="protected/quiz/questions/",
        null=True,
        blank=True
    )

    markdown = models.TextField(blank=True)
    rendered_html = models.TextField(blank=True, editable=False)

    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices
    )

    order = models.PositiveIntegerField()

    marks = models.FloatField(default=1)

    class Meta:
        ordering = ["order"]
        unique_together = [("quiz", "order")]

    def save(self, *args, **kwargs):
        if self.markdown:
            import markdown
            self.rendered_html = markdown.markdown(
                self.markdown,
                extensions=["fenced_code", "tables"]
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title[:50]

class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )

    text = models.TextField()

    is_correct = models.BooleanField(default=False)

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

class NumericAnswer(models.Model):

    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="numeric_answer"
    )

    min_value = models.FloatField()
    max_value = models.FloatField()