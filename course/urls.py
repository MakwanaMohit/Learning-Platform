from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from requests import delete
from course.models import Tag, Category
from course.views.CourseIndex import CourseListView
from course.views.CourseCreateUpdate import (CourseCreateView, CreateTagCatView, CourseUpdateView,
                                             VideoUploadView, VideoCompleteView)
from course.views.CourseDetail import CourseDetailView
from course.views.CreateUpdateChapter import ChapterCreateView, ChapterUpdateView
from course.views.CreateUpdateUnit import UnitCreateView, UnitUpdateView
from course.views.chapterContent import (ChapterContentView, create_content, update_content, delete_content, )
from course.views.quiz_content import create_quiz_item, update_quiz_item
from course.views.chapterList import ChapterListView
from course.views.delete import CourseDeleteView, UnitDeleteView, ChapterDeleteView


def temp(request, **kwargs):
    return HttpResponse(''.join(f'<h1>{slg}</h1>'for slg in kwargs.values()))


app_name = 'course'
urlpatterns = [
    path('',
         CourseListView.as_view(),
         name='Index Page'
         ),
    path('create/',
         CourseCreateView.as_view(),
         name='create_course'
         ),
    path('create-tag/',
         CreateTagCatView.as_view(model=Tag),
         name='create_tag'
         ),
    path('create-category/',
         CreateTagCatView.as_view(model=Category),
         name='create_category'
         ),
    path("demo-video/upload/",
         VideoUploadView.as_view(),
         name="demo_video_upload"
         ),
    path("demo-video/complete/",
         VideoCompleteView.as_view(),
         name="demo_video_complete"
         ),
    path('<slug:course_slug>/',
         CourseDetailView.as_view(),
         name='course_detail'
         ),
    path('<slug:course_slug>/change/',
         CourseUpdateView.as_view(),
         name='course_change'
         ),
    path('<slug:course_slug>/delete/',
         CourseDeleteView.as_view(),
         name='course_delete'
         ),
    path('<slug:course_slug>/unit/create/',
         UnitCreateView.as_view(),
         name='unit_create'
         ),
    path('<slug:course_slug>/unit/<slug:unit_slug>/change/',
         UnitUpdateView.as_view(),
         name='unit_change'
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/delete/",
         UnitDeleteView.as_view(),
         name="unit_delete"
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapter/",
         ChapterListView.as_view(),
         name="unit_chapter_list"
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapter/create/",
         ChapterCreateView.as_view(),
         name="chapter_create"
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapter/<slug:chapter_slug>/",
         temp,
         name="chapter_detail"
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapter/<slug:chapter_slug>/change/",
         ChapterUpdateView.as_view(),
         name="chapter_change"
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapter/<slug:chapter_slug>/delete/",
         ChapterDeleteView.as_view(),
         name="chapter_delete"
         ),
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapter/<slug:chapter_slug>/change-content/",
         ChapterContentView.as_view(),
         name="chapter_content_change"
         ),
    path("chapter-content/<slug:chapter_id>/add/",
         create_content,
         name="chapter_content_add"
         ),
    path("chapter-content/<slug:content_id>/change/",
         update_content,
         name="chapter_content_id_change"
         ),
    path("chapter-content/<slug:content_id>/delete/",
         delete_content,
         name="chapter_content_id_delete"
         ),
    path("chapter-content/<slug:content_id>/add-quiz/",
         create_quiz_item,
         name="chapter_quiz_add"
         ),
    path("chapter-content/<slug:content_id>/change-quiz/",
         update_quiz_item,
         name="chapter_quiz_change"
         ),
]
