from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


# Create your models here.


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def is_student(self):
        return self.role == 'student'

    def is_mentor(self):
        return self.role == 'mentor'

    def is_admin(self):
        return self.role == 'admin'

    def get_dashboard_url(self):
        return reverse("course:Index Page")

        if self.role == "student":
            return reverse("student:index")

        elif self.role == "mentor":
            return reverse("mentor:index")

        elif self.role == "admin":
            return reverse("admin:index")

        return reverse("accounts:login")
