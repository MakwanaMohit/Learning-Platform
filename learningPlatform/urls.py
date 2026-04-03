"""
URL configuration for learningPlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.index, name='index')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='index')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import path, include

from learningPlatform.tusd import tus_hook_view

urlpatterns = ([
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('course/', include(('course.urls','course'), namespace='course')),

    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("student/", include(("student.urls", "student"), namespace="student")),
    
    path("tus/hooks/", tus_hook_view, name="tus_hooks"),
    path("tus/finalize/", lambda request:JsonResponse({'msg':'hello'}), name="tus_hook_finalize"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +
               static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
               static(settings.PRIVATE_MEDIA_URL, document_root=settings.PRIVATE_MEDIA_ROOT))
