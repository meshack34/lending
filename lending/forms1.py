# lending/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

from .models import (
    MemberProfile, Loan, LoanPolicy,
    Company, Office, ManagerOfficerAssignment
)

User = get_user_model()


# =========================================================
# AUTH & LOGIN
# =========================================================
class CustomLoginForm(AuthenticationForm):
    """Custom login form styled with Bootstrap (email/phone + password)."""
    username = forms.CharField(
        label="Email or Phone",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email or phone number",
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


# =========================================================
# MEMBER REGISTRATION & PROFILE
# =========================================================
class MemberRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirm Password")
    national_id = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
        label="Date of Birth"
    )

    class Meta:
        model = User
        fields = ["first_name", "middle_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_password2(self):
        if self.cleaned_data.get("password1") != self.cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return self.cleaned_data.get("password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean_national_id(self):
        national_id = self.cleaned_data.get("national_id")
        if MemberProfile.objects.filter(national_id=national_id).exists():
            raise forms.ValidationError("National ID already exists.")
        return national_id

    def save(self, commit=True):
        user = super().save(commit=False)

        # Auto-generate username
        base_username = (self.cleaned_data["first_name"] + self.cleaned_data["last_name"]).lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username

        user.set_password(self.cleaned_data["password1"])
        user.role = "MEMBER"

        if commit:
            user.save()
            MemberProfile.objects.create(
                user=user,
                national_id=self.cleaned_data["national_id"],
                phone_number=self.cleaned_data["phone_number"],
                address=self.cleaned_data.get("address"),
                date_of_birth=self.cleaned_data.get("date_of_birth"),
            )
        return user


class MemberProfileForm(forms.ModelForm):
    """Allow members to update their profile except user + national_id."""
    class Meta:
        model = MemberProfile
        exclude = ["user", "national_id"]


# =========================================================
# LOAN APPLICATION & POLICY
# =========================================================
class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["policy", "principal_amount", "term_months", "purpose"]
        widgets = {
            "purpose": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member", None)
        super().__init__(*args, **kwargs)

        if self.member:
            office = getattr(self.member.user, "office", None)
            company = office.company if office else None
            if company:
                self.fields["policy"].queryset = company.loan_policies.all()
            else:
                self.fields["policy"].queryset = LoanPolicy.objects.none()

        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        policy = cleaned_data.get("policy")
        amount = cleaned_data.get("principal_amount")
        term = cleaned_data.get("term_months")

        if policy:
            if amount and (amount < policy.min_amount or amount > policy.max_amount):
                raise forms.ValidationError(
                    f"Loan amount must be between {policy.min_amount} and {policy.max_amount}."
                )
            if term and term > policy.max_term_months:
                raise forms.ValidationError(
                    f"Loan term cannot exceed {policy.max_term_months} months."
                )
        return cleaned_data


class LoanPolicyForm(forms.ModelForm):
    class Meta:
        model = LoanPolicy
        fields = ["company", "name", "interest_rate", "min_amount", "max_amount", "max_term_months"]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "interest_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "min_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "max_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "max_term_months": forms.NumberInput(attrs={"class": "form-control"}),
        }


# =========================================================
# COMPANY & OFFICE
# =========================================================
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "registration_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "registration_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class OfficeForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = ["company", "name", "location"]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
        }


# =========================================================
# ADMIN: USER MANAGEMENT
# =========================================================
class AdminUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Leave blank to keep current password (for edit)."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False
    )

    class Meta:
        model = User
        fields = ["first_name", "middle_name", "last_name", "email", "role", "office"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "office": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class AdminAssignOfficersForm(forms.Form):
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role="MANAGER"),
        label="Select Manager",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    officers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role="OFFICER"),
        label="Assign Officers",
        widget=forms.SelectMultiple(attrs={"class": "form-select"})
    )

    def save(self):
        manager = self.cleaned_data["manager"]
        officers = self.cleaned_data["officers"]

        # Remove old assignments
        ManagerOfficerAssignment.objects.filter(manager=manager).delete()
        # Add new
        for officer in officers:
            ManagerOfficerAssignment.objects.create(manager=manager, officer=officer)


# =========================================================
# REPORTING & SEARCH
# =========================================================
class ManagerReportForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    officer = forms.ModelChoiceField(
        queryset=User.objects.filter(role="OFFICER"),
        required=False,
        empty_label="All officers"
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All statuses")] + list(Loan.STATUS_CHOICES)
    )


class MemberSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "name, email, national id", "class": "form-control"})
    )
