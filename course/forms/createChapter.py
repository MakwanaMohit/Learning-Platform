from django import forms
from course.models import Chapter

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = ["course", "created_at","slug"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control form-control-sm",
                "placeholder": "Unit title",
                "style": "width:180px;"
            }),
            "order": forms.NumberInput(attrs={
                "class": "form-control form-control-sm",
                "style": "width:70px;"
            }),
        }