from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, MemberProfile


# Member Registration Form
class MemberRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    national_id = forms.CharField(max_length=20)
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "MEMBER"  # default role
        if commit:
            user.save()
            MemberProfile.objects.create(
                user=user,
                national_id=self.cleaned_data["national_id"],
                phone_number=self.cleaned_data["phone_number"],
                address=self.cleaned_data.get("address", ""),
            )
        return user


# Admin creates user with role
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]


# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput)
