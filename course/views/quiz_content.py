from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Max

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

from course.forms import QuestionForm, NumericQuestionForm, ChoiceForm
from course.models import ChapterContent, Question, NumericAnswer, Choice
from course.views import is_course_owner


@login_required
@require_GET
def create_quiz_item(request, content_id):

    creation_type = request.GET.get("creation_type",None)
    question_id = request.GET.get("question_id",None)

    content = get_object_or_404(
        ChapterContent.objects.select_related("chapter__unit__course").only(
            "id", "content_type", "chapter_id",
            "chapter__id", "chapter__unit_id",
            "chapter__unit__id", "chapter__unit__course_id",
            "chapter__unit__course__id",
            "chapter__unit__course__mentor_id",
        ),
        id=content_id
    )

    if not is_course_owner(request.user, content.chapter.unit.course):
        return JsonResponse({"error": "Permission denied"}, status=403)

    if content.content_type != "quiz":
        return JsonResponse({"error": "Invalid content type"}, status=400)

    quiz = content.quiz

    if not creation_type:
        return JsonResponse({"error": "creation type required"}, status=400)

    if creation_type == "mcq" or creation_type == "msq":

        max_order = quiz.questions.aggregate(
            Max("order")
        )["order__max"] or 0

        question = Question.objects.create(
            quiz=quiz,
            title="New Question",
            question_type=creation_type,
            order=max_order + 1,
            marks=1
        )
        question.form = QuestionForm(instance=question)

        html = render_to_string(
            "course/partials/question.html",
            {
                "question": question,
                'quiz': quiz,
            },
            request=request
        )

        return JsonResponse({"html": html})

    elif creation_type == "numeric":

        max_order = quiz.questions.aggregate(
            Max("order")
        )["order__max"] or 0

        question = Question.objects.create(
            quiz=quiz,
            title="New Numeric Question",
            question_type="numeric",
            order=max_order + 1,
            marks=1
        )

        numeric = NumericAnswer.objects.create(
            question=question,
            min_value=0,
            max_value=0
        )

        form = NumericQuestionForm(
            instance=question,
            numeric_instance=numeric
        )
        question.form = form

        html = render_to_string(
            "course/partials/question.html",
            {
                "question": question,
                "quiz":quiz,
            },
            request=request
        )

        return JsonResponse({"html": html})

    elif creation_type == "choice":

        if not question_id:
            return JsonResponse({"error": "question_id required"}, status=400)

        question = get_object_or_404(
            Question.objects.only("id", "question_type"),
            id=question_id,
            quiz=quiz
        )

        max_order = question.choices.aggregate(
            Max("order")
        )["order__max"] or 0

        choice = Choice.objects.create(
            question=question,
            text="New Choice",
            order=max_order + 1,
            is_correct=False
        )
        choice.form = ChoiceForm(instance=choice)
        html = render_to_string(
            "course/partials/choice.html",
            {
                "choice": choice,
                "question":choice.question,
                "quiz": quiz,
            },
            request=request
        )

        return JsonResponse({"html": html})

    return JsonResponse({"error": "Invalid creation type"}, status=400)


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def update_quiz_item(request, content_id):

    update_type = request.POST.get("update_type").strip()
    question_id = request.POST.get("question_id")
    choice_id = request.POST.get("choice_id")

    content = get_object_or_404(
        ChapterContent.objects.select_related("chapter__unit__course").only(
            "id", "content_type", "chapter_id",
            "chapter__id", "chapter__unit_id",
            "chapter__unit__id", "chapter__unit__course_id",
            "chapter__unit__course__id",
            "chapter__unit__course__mentor_id",
        ),
        id=content_id
    )

    if not is_course_owner(request.user, content.chapter.unit.course):
        return JsonResponse({"error": "Permission denied"}, status=403)

    if content.content_type != "quiz":
        return JsonResponse({"error": "Invalid content type"}, status=400)

    quiz = content.quiz

    if not update_type:
        return JsonResponse({"error": "update_type required"}, status=400)

    if update_type == "question":

        question = get_object_or_404(Question, id=question_id, quiz=quiz)

        form = QuestionForm(request.POST, request.FILES, instance=question)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        question = form.save()
        question.form = form

        html = render_to_string(
            "course/partials/question.html",
            {"question": question, "quiz": quiz},
            request=request
        )

        previewHtml = render_to_string(
            "course/partials/question_preview.html",
            {'question': question},
            request=request
        )

        return JsonResponse({"html": html,'previewHtml':previewHtml})


    elif update_type == "numeric":

        question = get_object_or_404(
            Question,
            id=question_id,
            quiz=quiz,
            question_type="numeric"
        )

        numeric = getattr(question, "numeric_answer", None)

        form = NumericQuestionForm(
            request.POST,
            request.FILES,
            instance=question,
            numeric_instance=numeric
        )
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        question = form.save()
        question.form = form

        html = render_to_string(
            "course/partials/question.html",
            {"question": question,'quiz': quiz},
            request=request
        )


        previewHtml = render_to_string(
            "course/partials/question_preview.html",
            {'question': question},
            request=request
        )

        return JsonResponse({"html": html,'previewHtml':previewHtml})

    elif update_type == "choice":

        choice = get_object_or_404(
            Choice.objects.select_related("question"),
            id=choice_id,
            question__quiz=quiz
        )

        form = ChoiceForm(request.POST, instance=choice)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        choice = form.save()
        choice.form = form

        html = render_to_string(
            "course/partials/choice.html",
            {"choice": choice,'question':choice.question,'quiz': quiz},
            request=request
        )

        previewHtml = render_to_string(
            "course/partials/question_preview.html",
            {'question': choice.question,quiz:quiz},
            request=request
        )

        return JsonResponse({"html": html,'previewHtml':previewHtml})


    return JsonResponse({"error": "Invalid update type"}, status=400)