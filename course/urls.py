from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from course.models import Tag, Category
from course.views import CourseListView
from course.views.CourseCreateUpdate import CourseCreateView, CreateTagCatView, CourseUpdateView, VideoUploadView, VideoCompleteView
from course.views.CourseDetail import CourseDetailView

from course.views.CreateUpdateUnit import UnitCreateView, UnitUpdateView
from course.views.chapterList import ChapterListView
from course.views.delete import CourseDeleteView, UnitDeleteView


def temp(request, course_slug, unit_slug):
    return HttpResponse(f'<h1>{course_slug}</h1><h1>{unit_slug}</h1>')


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
         )
    , path("demo-video/upload/",
           VideoUploadView.as_view(),
           name="demo_video_upload"
           ),
    path("demo-video/complete/",
         VideoCompleteView.as_view(),
         name="demo_video_complete"
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
    path("<slug:course_slug>/unit/<slug:unit_slug>/chapters/",
         ChapterListView.as_view(),
         name="unit_chapter_list"
         ),
]
