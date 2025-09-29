# lending/views/dashboards.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .mixins import admin_required, manager_required, officer_required, member_required

@login_required
@admin_required
def admin_dashboard(request):
    return render(request, "dashboard/admin.html")

@login_required
@manager_required
def manager_dashboard(request):
    return render(request, "dashboard/manager.html")

@login_required
@officer_required
def officer_dashboard(request):
    return render(request, "dashboard/officer.html")

