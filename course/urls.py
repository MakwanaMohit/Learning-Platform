from django.contrib import admin
from django.urls import path, include

from course.models import Tag, Category
from course.views import CourseListView
from course.views.CourseCreate import CourseCreateView, CreateTagCatView
from course.views.CourseDetail import CourseDetailView

app_name = 'course'
urlpatterns = [
    path('', CourseListView.as_view(), name='Index Page'),
    path('create', CourseCreateView.as_view(), name='create_course'),
    path('create-tag', CreateTagCatView.as_view(model = Tag), name='create_tag'),
    path('create-category', CreateTagCatView.as_view(model = Category), name='create_category'),

    path('<slug:course_slug>/', CourseDetailView.as_view(), name='course_detail'),
]