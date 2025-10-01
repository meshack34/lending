# lending/views/officer.py

import datetime
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum

from ..decorators import officer_required
from ..models import User, Loan, MemberProfile, Repayment, ReportLog


# -------------------------------
# Officer Dashboard
# -------------------------------
@login_required
@officer_required
def officer_dashboard(request):
    loans = Loan.objects.filter(officer=request.user)
    repayments = Repayment.objects.filter(loan__officer=request.user)

    stats = {
        "my_loans_total": loans.count(),
        "my_loans_pending": loans.filter(status="PENDING").count(),
        "my_loans_disbursed": loans.filter(status="DISBURSED").count(),
        "repayments_total": repayments.aggregate(Sum("amount"))["amount__sum"] or 0,
    }
    return render(request, "officer/dashboard.html", {"stats": stats})


# -------------------------------
# Members (in Officer’s office)
# -------------------------------
@login_required
@officer_required
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

    return render(request, "officer/member_list.html", {
        "members": members,
        "search_query": search,
    })


# -------------------------------
# Loan List
# -------------------------------
@login_required
@officer_required
def loan_list(request):
    loans = Loan.objects.filter(officer=request.user).select_related("member")

    status = request.GET.get("status")
    if status:
        loans = loans.filter(status=status)

    return render(request, "officer/loan_list.html", {
        "loans": loans,
        "status": status,
    })


# -------------------------------
# Loan Detail (approve/reject/disburse)
# -------------------------------
@login_required
@officer_required
def loan_detail(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, officer=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            loan.status = "APPROVED"
            loan.approved_at = datetime.datetime.now()
            loan.save()
            messages.success(request, "✅ Loan approved.")
        elif action == "reject":
            loan.status = "REJECTED"
            loan.save()
            messages.success(request, "❌ Loan rejected.")
        elif action == "disburse":
            if loan.status == "APPROVED":
                loan.status = "DISBURSED"
                loan.disbursed_at = datetime.datetime.now()
                loan.save()
                messages.success(request, "💸 Loan disbursed.")
            else:
                messages.error(request, "⚠️ Only approved loans can be disbursed.")

        return redirect("officer_loan_detail", loan_id=loan.id)

    repayments = loan.repayments.all()
    return render(request, "officer/loan_detail.html", {
        "loan": loan,
        "repayments": repayments,
    })


# -------------------------------
# Repayment List (Officer’s loans only)
# -------------------------------
@login_required
@officer_required
def repayment_list(request):
    repayments = Repayment.objects.filter(loan__officer=request.user).select_related("loan")

    return render(request, "officer/repayment_list.html", {
        "repayments": repayments,
    })


# -------------------------------
# Reports (Officer-level)
# -------------------------------
@login_required
@officer_required
def report_list(request):
    loans = Loan.objects.filter(officer=request.user)
    reports = {
        "total_loans": loans.count(),
        "active_loans": loans.exclude(status__in=["CLOSED", "REJECTED"]).count(),
        "closed_loans": loans.filter(status="CLOSED").count(),
        "pending_loans": loans.filter(status="PENDING").count(),
        "overdue_loans": loans.filter(balance__gt=0, status="DISBURSED").count(),
        "total_repayments": Repayment.objects.filter(loan__in=loans).aggregate(Sum("amount"))["amount__sum"] or 0,
    }

    # log officer report
    ReportLog.objects.create(
        generated_by=request.user,
        report_type="Officer Performance Report"
    )

    return render(request, "officer/report_list.html", {"reports": reports})
