from django import forms

from chunked_upload.models import ChunkedUpload
from course.models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "short_description",
            "description",
            "thumbnail",
            "category",
            "keywords",
            "mentors",
            "level",
            "status",
            "is_free",
            "price",
            "duration_hours",
        ]

        widgets = {
            "keywords": forms.SelectMultiple(attrs={
                "class": "form-select",
                "size": "6"
            }),
            "demo_video": forms.ClearableFileInput(attrs={
                "accept": "video/mp4",
                "class": "form-control"
            }),

        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if self.request:
            self.fields["mentors"].queryset = self.fields["mentors"].queryset.exclude(
                pk=self.request.user.pk
            )

    def clean(self):
        cleaned_data = super().clean()

        mentors = cleaned_data.get("mentors")

        if self.request and mentors:
            if self.request.user in mentors:
                self.add_error(
                    "mentors",
                    "You cannot add yourself as a co-mentor."
                )

        return cleaned_data