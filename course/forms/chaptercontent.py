from django import forms
from course.models import MarkdownContent, Quiz, Question, Choice, NumericAnswer, VideoContent
from course.models.chapter_content import Assignment


class MarkdownForm(forms.ModelForm):
    class Meta:
        model = MarkdownContent
        fields = ["title", "markdown_content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "markdown_content": forms.Textarea(attrs={"rows": 4}),
        }
class VideoForm(forms.ModelForm):
    class Meta:
        model = VideoContent
        fields = ["title",]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title",]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }