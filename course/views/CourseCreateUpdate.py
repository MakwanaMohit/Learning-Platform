import shutil
import uuid

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.context_processors import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from docutils.nodes import field

from chunked_upload.models import ChunkedUpload
from course.forms import CourseForm
from accounts.views import RoleRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from course.models import Course
from course.views import is_course_owner
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
import os
from django.core.files.base import File

from course.views.mixins import CourseChangeAccessMixin


class CreateTagCatView(View):
    model = None  # passed from urls

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            return JsonResponse({"error": "Name is required"}, status=400)

        obj, created = self.model.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name)}
        )

        return JsonResponse({
            "id": obj.id,
            "name": obj.name,
            "created": created
        })


class CourseCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"
    success_url = reverse_lazy("course:Index Page")
    allowed_roles = ['mentor']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.mentor = self.request.user

        upload_id = self.request.POST.get("upload_id")
        file_name = self.request.POST.get("uploaded_file_name")

        response = super().form_valid(form)

        instance = self.object

        if not upload_id:
            return response

        try:
            temp_obj = ChunkedUpload.objects.get(upload_id=upload_id)
        except ChunkedUpload.DoesNotExist:
            return response

        temp_file = temp_obj.file

        if not temp_file:
            temp_obj.delete()
            return response

        temp_file.close()
        instance.demo_video.name = temp_obj.file.name
        instance.save(update_fields=["demo_video"])
        temp_obj.delete(delete_file=False)
        return response

class CourseUpdateView(LoginRequiredMixin, RoleRequiredMixin, CourseChangeAccessMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"
    allowed_roles = ["mentor"]


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


    def form_valid(self, form):
        chunk_id = self.request.POST.get("upload_id")
        file_name = self.request.POST.get("uploaded_file_name")
        response = super().form_valid(form)
        instance = self.object
        if not chunk_id:
            return response

        try:
            temp_obj = ChunkedUpload.objects.get(upload_id=chunk_id)
        except ChunkedUpload.DoesNotExist:
            messages.error(self.request, "Invalid temporary video.")
            return self.form_invalid(form)

        temp_file = temp_obj.file

        if not temp_file:
            messages.error(self.request, "No file found.")
            return self.form_invalid(form)

        temp_file.close()

        if self.object and self.object.demo_video:
            self.object.demo_video.delete(save=False)

        instance.demo_video.name = temp_obj.file.name
        instance.save(update_fields=["demo_video"])
        temp_obj.delete(delete_file=False)

        return response

    def get_success_url(self):
        # Redirect back to the course detail page using the slug
        return self.object.get_absolute_url()

class VideoUploadView(ChunkedUploadView):
    field_name = "file"
    file_field = 'demo_video'
    model_class = Course

    def check_permissions(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'mentor':
            raise PermissionDenied("Not allowed")


class VideoCompleteView(ChunkedUploadCompleteView):
    do_md5_check = False
    response_data = {}
    
    file_field = 'demo_video'
    model_class = Course

    def check_permissions(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'mentor':
            raise PermissionDenied("Not allowed")

    def on_completion(self, uploaded_file, request):
        uploaded_file.close()
        self.response_data.update({
            "file_name": uploaded_file.name,
            "file_size": uploaded_file.size,
        })
        print(self.response_data)
        pass

    def get_response_data(self, chunked_upload, request):
        data = self.response_data if self.response_data else {
            "file_name": chunked_upload.file.name,
            "file_size": chunked_upload.file.size,
        }
        data.update( {
            "upload_id": chunked_upload.upload_id,
            "file_url": chunked_upload.file.url,
        })
        return data
