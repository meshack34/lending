# lending/views/admin.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import CompanyForm, OfficeForm
from .mixins import admin_required
from ..models import Company, Office, User, Loan


@login_required
@admin_required
def admin_dashboard(request):
    stats = {
        "companies": Company.objects.count(),
        "offices": Office.objects.count(),
        "users": User.objects.count(),
        "loans": Loan.objects.count(),
    }
    return render(request, "admin/dashboard.html", {"stats": stats})

@login_required
@admin_required
def company_list(request):
    companies = Company.objects.all()
    return render(request, "admin/company_list.html", {"companies": companies})

@login_required
@admin_required
def company_create(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Company created.")
            return redirect("company_list")
    else:
        form = CompanyForm()
    return render(request, "admin/company_form.html", {"form": form})

@login_required
@admin_required
def office_list(request):
    offices = Office.objects.select_related("company").all()
    return render(request, "admin/office_list.html", {"offices": offices})

@login_required
@admin_required
def office_create(request):
    if request.method == "POST":
        form = OfficeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Office created.")
            return redirect("office_list")
    else:
        form = OfficeForm()
    return render(request, "admin/office_form.html", {"form": form})
