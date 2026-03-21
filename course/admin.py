from django.contrib import admin

# Register your models here.
from django.contrib import admin

from course.models.course import (
    Category, Tag, Course
)
from course.models.chapter_content import (
ChapterContent, MarkdownContent, VideoContent
)
from course.models.quiz import (
Quiz, Question, Choice, NumericAnswer,
)
from course.models.unit import Unit
from course.models.chapter import Chapter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    pass


@admin.register(ChapterContent)
class ChapterContentAdmin(admin.ModelAdmin):
    pass


@admin.register(MarkdownContent)
class MarkdownContentAdmin(admin.ModelAdmin):
    pass


@admin.register(VideoContent)
class VideoContentAdmin(admin.ModelAdmin):
    pass


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(NumericAnswer)
class NumericAnswerAdmin(admin.ModelAdmin):
    pass