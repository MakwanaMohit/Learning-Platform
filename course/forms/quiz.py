from django import forms
from course.models import Quiz, Question, Choice, NumericAnswer

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description"]

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "image", "markdown", "marks"]

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["text", "is_correct"]

    def save(self, commit=True):
        choice = super().save(commit)

        question = choice.question

        if choice.is_correct and question.question_type == "mcq":
            Choice.objects.filter(
                question=question,
                is_correct=True
            ).exclude(pk=choice.pk).update(is_correct=False)

        return choice

class NumericQuestionForm(forms.ModelForm):
    min_value = forms.FloatField()
    max_value = forms.FloatField()

    class Meta:
        model = Question
        fields = ["title",'image', "markdown", "marks"]

    def __init__(self, *args, **kwargs):
        self.numeric_instance = kwargs.pop("numeric_instance", None)
        super().__init__(*args, **kwargs)

        # preload numeric values
        if self.numeric_instance:
            self.fields["min_value"].initial = self.numeric_instance.min_value
            self.fields["max_value"].initial = self.numeric_instance.max_value

    def save(self, commit=True):
        question = super().save(commit)

        numeric, created = NumericAnswer.objects.get_or_create(
            question=question
        )

        numeric.min_value = self.cleaned_data["min_value"]
        numeric.max_value = self.cleaned_data["max_value"]

        if commit:
            numeric.save()

        return question