from django.contrib import admin
from django.urls import path, include
from core.views import IndexView

app_name = 'core'
urlpatterns = [
    path('',IndexView.as_view(),name='home'),
]