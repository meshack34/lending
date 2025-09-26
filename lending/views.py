from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, MemberProfile, Loan, Repayment, LoanPolicy
from .forms import MemberRegisterForm, LoginForm, UserCreateForm


def home(request):
    return render(request, "lending/home.html")


# -------------------------------
# Registration (Member)
# -------------------------------
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = MemberRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")
    else:
        form = MemberRegisterForm()

    return render(request, "lending/auth/register.html", {"form": form})


# -------------------------------
# Login
# -------------------------------
def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = LoginForm()

    return render(request, "lending/auth/login.html", {"form": form})


# -------------------------------
# Logout
# -------------------------------
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")


# -------------------------------
# Admin Create User
# -------------------------------
@login_required
def admin_create_user(request):
    # Make sure is_admin() is implemented in your User model
    if not request.user.is_admin():
        messages.error(request, "Unauthorized access.")
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect("dashboard")
    else:
        form = UserCreateForm()

    return render(request, "lending/auth/admin_create_user.html", {"form": form})
