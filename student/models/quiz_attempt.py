from django.db import models

class QuizAttempt(models.Model):

    enrollment = models.ForeignKey(
        'Enrollment',
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        db_index=True
    )

    quiz = models.ForeignKey(
        "course.Quiz",
        on_delete=models.CASCADE,
        related_name="attempts",
        db_index=True
    )

    attempt_number = models.PositiveIntegerField()

    score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "quiz", "attempt_number"],
                name="unique_attempt_per_number"
            )
        ]

        indexes = [
            models.Index(fields=["enrollment", "quiz"]),
            models.Index(fields=["quiz", "score"]),
        ]


class QuestionResponse(models.Model):

    attempt = models.ForeignKey(
        'QuizAttempt',
        on_delete=models.CASCADE,
        related_name="responses",
        db_index=True
    )

    question = models.ForeignKey(
        "course.Question",
        on_delete=models.CASCADE,
        related_name="responses",
        db_index=True
    )

    # For numeric questions
    numeric_answer = models.FloatField(null=True, blank=True)

    is_correct = models.BooleanField(default=False)
    marks_awarded = models.FloatField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_question_per_attempt"
            )
        ]

        indexes = [
            models.Index(fields=["attempt", "question"]),
        ]

class SelectedChoice(models.Model):

    response = models.ForeignKey(
        'QuestionResponse',
        on_delete=models.CASCADE,
        related_name="selected_choices",
        db_index=True
    )

    choice = models.ForeignKey(
        "course.Choice",
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["response", "choice"],
                name="unique_choice_per_response"
            )
        ]