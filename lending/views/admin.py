# lending/views/admin.py

import csv
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from ..decorators import admin_required
from ..forms import ( CompanyForm,OfficeForm, AdminUserForm,AdminAssignOfficersForm,LoanPolicyForm,
)
from ..models import (Company,Office,User,Loan,MemberProfile,ManagerOfficerAssignment,LoanPolicy,ReportLog,
)


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
def company_edit(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Company updated successfully.")
            return redirect("company_list")
    else:
        form = CompanyForm(instance=company)
    return render(request, "admin/company_form.html", {"form": form, "title": "Edit Company"})

@login_required
@admin_required
def company_delete(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, "✅ Company deleted successfully.")
    return redirect("company_list")

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


@login_required
@admin_required
def office_edit(request, office_id):
    office = get_object_or_404(Office, id=office_id)
    if request.method == "POST":
        form = OfficeForm(request.POST, instance=office)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Office updated successfully.")
            return redirect("office_list")
    else:
        form = OfficeForm(instance=office)
    return render(request, "admin/office_form.html", {"form": form, "title": "Edit Office"})

@login_required
@admin_required
def office_delete(request, office_id):
    office = get_object_or_404(Office, id=office_id)
    office.delete()
    messages.success(request, "✅ Office deleted successfully.")
    return redirect("office_list")




# Loan Policies
@login_required
@admin_required
def policy_list(request):
    policies = LoanPolicy.objects.select_related("company").all()
    return render(request, "admin/policy_list.html", {"policies": policies})


@login_required
@admin_required
def policy_create(request):
    from ..forms import LoanPolicyForm  # make sure the form is imported

    if request.method == "POST":
        form = LoanPolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Loan Policy created successfully.")
            return redirect("policy_list")
    else:
        form = LoanPolicyForm()

    return render(request, "admin/policy_form.html", {"form": form})

# Reports
@login_required
@admin_required
def report_list(request):
    reports = ReportLog.objects.select_related("generated_by").order_by("-created_at")
    return render(request, "admin/report_list.html", {"reports": reports})





# -------------------------------
# User Create
# -------------------------------
@login_required
@admin_required
def user_create(request):
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ User created successfully.")
            return redirect("user_list")
    else:
        form = AdminUserForm()
    return render(request, "admin/user_form.html", {"form": form, "title": "Create User"})


# -------------------------------
# User Edit
# -------------------------------
@login_required
@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ User updated successfully.")
            return redirect("user_list")
    else:
        form = AdminUserForm(instance=user)
    return render(request, "admin/user_form.html", {"form": form, "title": "Edit User"})


@login_required
@admin_required
def user_list(request):
    role = request.GET.get("role")
    search = request.GET.get("q")

    users = User.objects.select_related("office").all()

    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )

    roles = User.ROLE_CHOICES
    return render(request, "admin/user_list.html", {
        "users": users,
        "roles": roles,
        "selected_role": role,
        "search_query": search,
    })

@login_required
@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "❌ Cannot delete superuser.")
        return redirect("user_list")
    user.delete()
    messages.success(request, "✅ User deleted successfully.")
    return redirect("user_list")



@login_required
@admin_required
def assign_officers_to_manager(request):
    if request.method == "POST":
        form = AdminAssignOfficersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Officers assigned to Manager successfully.")
            return redirect("assign_officers")
    else:
        form = AdminAssignOfficersForm()

    # Optional: show current assignments for info
    assignments = ManagerOfficerAssignment.objects.select_related("manager", "officer").all()
    
    return render(request, "admin/assign_officers.html", {
        "form": form,
        "assignments": assignments,
        "title": "Assign Officers to Manager"
    })


# -------------------------------
# Member Management
# -------------------------------


# -------------------------------
# Create Member
# -------------------------------
@login_required
@admin_required
def member_create(request):
    from ..forms import MemberRegistrationForm

    if request.method == "POST":
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            member_profile = form.save(commit=False)
            # Ensure the related user is active by default
            member_profile.user.is_active = True
            member_profile.user.save()
            member_profile.save()
            messages.success(request, "✅ Member created successfully.")
            return redirect("member_list")
    else:
        form = MemberRegistrationForm()

    return render(request, "admin/member_form.html", {"form": form, "title": "Create Member"})


# -------------------------------
# Edit Member
# -------------------------------
@login_required
@admin_required
def member_edit(request, member_id):
    member_profile = get_object_or_404(MemberProfile, id=member_id)
    from ..forms import MemberProfileForm

    if request.method == "POST":
        form = MemberProfileForm(request.POST, instance=member_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Member updated successfully.")
            return redirect("member_list")
    else:
        form = MemberProfileForm(instance=member_profile)

    return render(request, "admin/member_form.html", {"form": form, "title": "Edit Member"})


# -------------------------------
# Suspend / Activate Member
# -------------------------------
@login_required
@admin_required
def member_suspend(request, member_id):
    member_profile = get_object_or_404(MemberProfile, id=member_id)
    
    # Toggle the related user's is_active status
    member_profile.user.is_active = not member_profile.user.is_active
    member_profile.user.save()

    status = "suspended" if not member_profile.user.is_active else "activated"
    messages.success(request, f"✅ Member {status} successfully.")
    return redirect("member_list")




# -------------------------------
# List Members
# -------------------------------
@login_required
@admin_required
def member_list(request):
    search = request.GET.get("q")
    members = MemberProfile.objects.select_related("user").all()

    if search:
        members = members.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(national_id__icontains=search)
        )

    return render(request, "admin/member_list.html", {
        "members": members,
        "search_query": search,
    })


# -------------------------------
# Export Members to CSV
# -------------------------------
@login_required
@admin_required
def export_members_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="members_{datetime.date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'National ID', 'Active'])

    for member in MemberProfile.objects.select_related("user").all():
        writer.writerow([
            member.id,
            f"{member.user.first_name} {member.user.last_name}",
            member.user.email,
            member.phone_number,
            member.national_id,
            "Yes" if member.user.is_active else "No"  # Correctly reflects active status
        ])

    return response
