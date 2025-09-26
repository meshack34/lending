from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("OFFICER", "Loan Officer"),
        ("MEMBER", "Member"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="MEMBER")

    def is_admin(self):
        return self.role == "ADMIN"

    def is_officer(self):
        return self.role == "OFFICER"

    def is_member(self):
        return self.role == "MEMBER"

    def __str__(self):
        return f"{self.username} ({self.role})"
