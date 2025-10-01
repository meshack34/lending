# lending/views/manager.py

import datetime
import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count

from ..decorators import manager_required
from ..models import (
    User, Loan, MemberProfile, Repayment, ManagerOfficerAssignment, ReportLog
)


# -------------------------------
# Dashboard
# -------------------------------
@login_required
@manager_required
def manager_dashboard(request):
    # Manager should only see stats for their own office
    office = request.user.office
    officers = User.objects.filter(role="OFFICER", office=office)
    officer_ids = officers.values_list("id", flat=True)

    loans = Loan.objects.filter(officer_id__in=officer_ids)
    repayments = Repayment.objects.filter(loan__officer_id__in=officer_ids)

    stats = {
        "officers_count": officers.count(),
        "members_count": MemberProfile.objects.filter(user__office=office).count(),
        "loans_total": loans.count(),
        "loans_pending": loans.filter(status="PENDING").count(),
        "loans_disbursed": loans.filter(status="DISBURSED").count(),
        "repayments_total": repayments.aggregate(total=Sum("amount"))["total"] or 0,
    }

    return render(request, "manager/dashboard.html", {"stats": stats})


# -------------------------------
# Officers under this Manager
# -------------------------------
@login_required
@manager_required
def officer_list(request):
    office = request.user.office
    officers = User.objects.filter(role="OFFICER", office=office)

    return render(request, "manager/officer_list.html", {
        "officers": officers,
        "office": office,
    })


# -------------------------------
# Members in this Manager’s office
# -------------------------------
@login_required
@manager_required
def member_list(request):
    office = request.user.office
    search = request.GET.get("q")

    members = MemberProfile.objects.filter(user__office=office).select_related("user")

    if search:
        members = members.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(national_id__icontains=search)
        )

    return render(request, "manager/member_list.html", {
        "members": members,
        "search_query": search,
    })


# -------------------------------
# Loans under this Manager’s office
# -------------------------------
@login_required
@manager_required
def loan_list(request):
    office = request.user.office
    loans = Loan.objects.filter(officer__office=office).select_related("member", "officer")

    status = request.GET.get("status")
    if status:
        loans = loans.filter(status=status)

    return render(request, "manager/loan_list.html", {
        "loans": loans,
        "status": status,
    })


@login_required
@manager_required
def loan_detail(request, loan_id):
    office = request.user.office
    loan = get_object_or_404(Loan, id=loan_id, officer__office=office)

    repayments = loan.repayments.all()

    return render(request, "manager/loan_detail.html", {
        "loan": loan,
        "repayments": repayments,
    })


# -------------------------------
# Repayments overview
# -------------------------------
@login_required
@manager_required
def repayment_list(request):
    office = request.user.office
    repayments = Repayment.objects.filter(loan__officer__office=office).select_related("loan")

    return render(request, "manager/repayment_list.html", {
        "repayments": repayments,
    })


# -------------------------------
# Reports (Office-level)
# -------------------------------
@login_required
@manager_required
def report_list(request):
    office = request.user.office
    officers = User.objects.filter(role="OFFICER", office=office)
    loans = Loan.objects.filter(officer__in=officers)

    reports = {
        "total_loans": loans.count(),
        "active_loans": loans.exclude(status__in=["CLOSED", "REJECTED"]).count(),
        "closed_loans": loans.filter(status="CLOSED").count(),
        "pending_loans": loans.filter(status="PENDING").count(),
        "overdue_loans": loans.filter(balance__gt=0, status="DISBURSED").count(),
        "total_repayments": Repayment.objects.filter(loan__in=loans).aggregate(Sum("amount"))["amount__sum"] or 0,
    }

    # Log report
    ReportLog.objects.create(
        generated_by=request.user,
        report_type="Manager Office Report"
    )

    return render(request, "manager/report_list.html", {"reports": reports})


# -------------------------------
# Export members/loans to CSV
# -------------------------------
@login_required
@manager_required
def export_members_csv(request):
    office = request.user.office
    members = MemberProfile.objects.filter(user__office=office)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="members_office_{office.id}_{datetime.date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'National ID'])

    for m in members:
        writer.writerow([
            m.id,
            f"{m.user.first_name} {m.user.last_name}",
            m.user.email,
            m.phone_number,
            m.national_id,
        ])

    return response
