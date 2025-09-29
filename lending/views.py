# lending/views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from .models import Loan, LoanPolicy  # add LoanPolicy here
from .forms import CustomLoginForm, MemberRegistrationForm

User = get_user_model()
