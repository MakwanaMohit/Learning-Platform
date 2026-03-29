# templatetags/content_tags.py
from django import template
from django.template.loader import render_to_string

from course.forms.chaptercontent import VideoForm, AssignmentForm
from course.models import MarkdownContent, Quiz
from course.forms import (
    MarkdownForm, QuizForm, QuestionForm,
    ChoiceForm, NumericQuestionForm
)
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag(takes_context=True)
def render_content(context, content):
    request = context["request"]

    if content.content_type == "markdown":
        obj = content.markdowncontent

        html = render_to_string(
            "course/partials/markdown.html",
            {
                "content": obj,
                "form": MarkdownForm(instance=obj),
            },
            request=request
        )

        return mark_safe(html)
    elif content.content_type == "video":
        obj = content.videocontent

        html = render_to_string(
            "course/partials/video.html",
            {
                "content": obj,
                "form": VideoForm(instance=obj),
            },
            request=request
        )

        return mark_safe(html)
    elif content.content_type == "assignment":
        obj = content.assignment

        html = render_to_string(
            "course/partials/assignment.html",
            {
                "content": obj,
                "form": AssignmentForm(instance=obj),
            },
            request=request
        )

        return mark_safe(html)

    elif content.content_type == "quiz":
        quiz = content.quiz

        questions = quiz.questions.all()

        for q in questions:
            # ✅ Numeric question → combined form
            if q.question_type == "numeric":
                q.form = NumericQuestionForm(
                    instance=q,
                    numeric_instance=getattr(q, "numeric_answer", None)
                )

            # ✅ MCQ / MSQ
            else:
                q.form = QuestionForm(instance=q)
                q.choices_copy = q.choices.all()

                # attach choice forms
                for c in q.choices_copy:
                    c.form = ChoiceForm(instance=c)

        html = render_to_string(
            "course/partials/quiz.html",
            {
                "quiz": quiz,
                "quiz_form": QuizForm(instance=quiz),
                "questions": questions,  # optional but cleaner
            },
            request=request
        )

        return mark_safe(html)

    return ""