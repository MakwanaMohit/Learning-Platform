from django.contrib import admin
from django.urls import path, include
from student.views.index import StudentDashboardView

app_name = 'student'
urlpatterns = [
    path('',StudentDashboardView.as_view(),name='index'),
]