from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import MemberProfile, Loan

User = get_user_model()


# -------------------------------
# Login Form
# -------------------------------
class CustomLoginForm(AuthenticationForm):
    """Custom login form styled with Bootstrap."""
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your username",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password",
        }),
    )


# -------------------------------
# Member Registration
# -------------------------------
class MemberRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    national_id = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_password2(self):
        if self.cleaned_data.get("password1") != self.cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return self.cleaned_data.get("password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = "MEMBER"
        if commit:
            user.save()
            MemberProfile.objects.create(
                user=user,
                national_id=self.cleaned_data["national_id"],
                phone_number=self.cleaned_data["phone_number"],
                address=self.cleaned_data.get("address"),
            )
        return user


# -------------------------------
# Member Profile Update
# -------------------------------
class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        exclude = ["user", "national_id"]


# -------------------------------
# Loan Application
# -------------------------------
class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["policy", "principal_amount", "term_months", "purpose"]

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member", None)
        super().__init__(*args, **kwargs)

        if self.member:
            company = self.member.user.office.company if self.member.user.office else None
            if company:
                self.fields["policy"].queryset = company.loan_policies.all()
