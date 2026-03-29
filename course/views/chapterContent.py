from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Max

from course.forms.chaptercontent import VideoForm, AssignmentForm
from course.models import ChapterContent, NumericAnswer, Choice, VideoContent
from course.forms import MarkdownForm, QuizForm
from course.forms.quiz import NumericQuestionForm, QuestionForm, ChoiceForm
from course.models import Chapter, ChapterContent, MarkdownContent, Question
from course.models import Quiz
from course.models import Chapter
from course.models.chapter_content import Assignment
from course.views import is_course_owner
from course.views.mixins import ChapterChangeAccessMixin


class ChapterContentView(
    LoginRequiredMixin,
    ChapterChangeAccessMixin,  # your custom access control
    DetailView
):
    model = Chapter
    template_name = "course/chapter_content.html"
    context_object_name = "chapter"
    slug_field = "slug"
    slug_url_kwarg = "chapter_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        chapter = self.chapter
        unit = chapter.unit
        course = unit.course

        context.update({
            "unit": unit,
            "course": course,
            "chapter": chapter,
            "types": ChapterContent.ContentType.choices
        })

        return context


@login_required
@require_GET
def create_content(request, chapter_id):
    content_type = request.GET.get("type")

    chapter = get_object_or_404(
        Chapter.objects.select_related("unit__course").only(
            "id", "unit_id",
            "unit__id", "unit__course_id",
            "unit__course__id",
            "unit__course__mentor_id",
        ),
        id=chapter_id
    )

    if not is_course_owner(request.user, chapter.unit.course):
        return JsonResponse({"error": "Permission denied"}, status=403)

    max_order = chapter.contents.aggregate(
        Max("order")
    )["order__max"] or 0

    order = max_order + 1

    if content_type == "markdown":
        content = MarkdownContent.objects.create(
            chapter=chapter,
            order=order,
            title="",
            markdown_content=""
        )

    elif content_type == "quiz":
        content = Quiz.objects.create(
            chapter=chapter,
            order=order,
            title="New Quiz",
            description=""
        )
    elif content_type == 'video':
        content = VideoContent.objects.create(
            chapter=chapter,
            order=order,
            title="New Video Content",

        )
    elif content_type == "assignment":
        content = Assignment.objects.create(
            chapter=chapter,
            order=order,
            title="New Assignment",
        )
    else:
        return JsonResponse({"error": "Invalid type"}, status=400)

    html = render_to_string(
        "course/partials/content_wrapper.html",
        {"content": content},
        request=request
    )

    return JsonResponse({"html": html})


@login_required
@require_POST
def update_content(request, content_id):
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

    # resolve child model
    if content.content_type == "markdown":
        obj = content.markdowncontent
        form = MarkdownForm(request.POST, instance=obj)
    elif content.content_type == "video":
        obj = content.videocontent
        form = VideoForm(request.POST, instance=obj)
    elif content.content_type == "assignment":
        obj = content.assignment
        form = AssignmentForm(request.POST, instance=obj)

    elif content.content_type == "quiz":
        obj = content.quiz
        form = QuizForm(request.POST, instance=obj)

    else:
        return JsonResponse({"error": "Invalid type"}, status=400)

    if form.is_valid():
        form.save()

        html = render_to_string(
            "course/partials/content_wrapper.html",
            {"content": content},
            request=request
        )

        return JsonResponse({"html": html})

    return JsonResponse({"errors": form.errors}, status=400)


@login_required
@require_POST
def delete_content(request, content_id):
    delete_type = request.POST.get('delete_type')
    question_id = request.POST.get('questionId')
    choice_id = request.POST.get('choiceId')

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

    if not delete_type:
        return JsonResponse({"error": "delete_type required"}, status=400)

    if not is_course_owner(request.user, content.chapter.unit.course):
        return JsonResponse({"error": "Permission denied"}, status=403)

    # ---------------- DELETE CONTENT ----------------
    if delete_type == 'content':
        obj_map = {
            "markdown": "markdowncontent",
            "video": "videocontent",
            "assignment": "assignment",
            "quiz": "quiz",
        }

        attr = obj_map.get(content.content_type)
        if not attr:
            return JsonResponse({"error": "Invalid content type"}, status=400)

        obj = getattr(content, attr, None)
        if not obj:
            return JsonResponse({"error": "Object not found"}, status=404)

        obj.delete()
        return JsonResponse({'success': True}, status=200)

    # ---------------- DELETE QUESTION ----------------
    elif delete_type == 'question':
        if content.content_type != "quiz":
            return JsonResponse({"error": "Not a quiz content"}, status=400)

        if not question_id:
            return JsonResponse({"error": "questionId required"}, status=400)

        deleted, _ = Question.objects.filter(
            id=question_id,
            quiz_id=content_id
        ).delete()

        if not deleted:
            return JsonResponse({"error": "Question not found"}, status=404)

        return JsonResponse({'success': True}, status=200)

    # ---------------- DELETE CHOICE (SINGLE QUERY) ----------------
    elif delete_type == 'choice':
        if content.content_type != "quiz":
            return JsonResponse({"error": "Not a quiz content"}, status=400)

        if not question_id or not choice_id:
            return JsonResponse(
                {"error": "questionId and choiceId required"},
                status=400
            )

        deleted, _ = Choice.objects.filter(
            id=choice_id,
            question_id=question_id,
            question__quiz_id=content_id
        ).delete()

        if not deleted:
            return JsonResponse({"error": "Choice not found"}, status=404)

        return JsonResponse({'success': True}, status=200)

    return JsonResponse({"error": "Invalid delete_type"}, status=400)
