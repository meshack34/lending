# lending/views/auth.py

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from ..forms import CustomLoginForm, MemberRegistrationForm

User = get_user_model()

def home(request):
    return render(request, "lending/home.html")

class CustomLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomLoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_admin():
            return "/dashboard/admin/"
        elif user.is_manager():
            return "/dashboard/manager/"
        elif user.is_officer():
            return "/dashboard/officer/"
        return "/dashboard/member/"

class CustomLogoutView(LogoutView):
    next_page = "/login/"

def member_register(request):
    if request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("member_dashboard")
    else:
        form = MemberRegistrationForm()

    return render(request, "auth/register_member.html", {"form": form})
