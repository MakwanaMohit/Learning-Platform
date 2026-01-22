from django.contrib import admin
from django.urls import path, include
from course.views import CourseIndexView

urlpatterns = [
    path('',CourseIndexView.as_view(),name='Index Page'),
]