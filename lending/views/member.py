# lending/views/member.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from ..models import Loan, Repayment, MemberProfile, LoanPolicy
from ..forms import MemberProfileForm, LoanApplicationForm
from .mixins import member_required

@login_required
@member_required
def member_dashboard(request):
    profile = getattr(request.user, "profile", None)
    loans = Loan.objects.filter(member=profile).order_by("-created_at")
    active_loans = loans.filter(status__in=["PENDING", "APPROVED", "DISBURSED"])
    closed_loans = loans.filter(status="CLOSED")
    repayments = Repayment.objects.filter(loan__member=profile).order_by("-paid_at")
    recent_repayments = repayments[:5]

    total_loans = loans.count()
    total_principal = loans.aggregate(total=Sum("principal_amount"))["total"] or 0
    total_repaid = repayments.aggregate(total=Sum("amount"))["total"] or 0
    outstanding_balance = max(total_principal - total_repaid, 0)

    repayment_trend = (
        repayments.annotate(month=TruncMonth("paid_at"))
        .values("month").annotate(total=Sum("amount")).order_by("month")
    )

    return render(request, "dashboard/member.html", {
        "profile": profile,
        "active_loans": active_loans,
        "closed_loans": closed_loans,
        "recent_repayments": recent_repayments,
        "total_loans": total_loans,
        "total_principal": total_principal,
        "total_repaid": total_repaid,
        "outstanding_balance": outstanding_balance,
        "repayment_trend": repayment_trend,
    })

@login_required
@member_required
def member_profile(request):
    profile = get_object_or_404(MemberProfile, user=request.user)
    if request.method == "POST":
        form = MemberProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("member_profile")
    else:
        form = MemberProfileForm(instance=profile)
    return render(request, "member/profile.html", {"form": form})

# views/member_loans.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from lending.models import MemberProfile, Loan
from lending.forms import LoanApplicationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import LoanPolicy, MemberProfile, Loan
from ..forms import LoanApplicationForm
from ..decorators import member_required

@login_required
@member_required
def loan_apply(request):
    profile = get_object_or_404(MemberProfile, user=request.user)
    if request.method == "POST":
        form = LoanApplicationForm(request.POST, member=profile)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = profile
            loan.interest_rate = loan.policy.interest_rate
            loan.save()
            messages.success(request, "✅ Loan application submitted successfully.")
            return redirect("loan_list")
    else:
        form = LoanApplicationForm(member=profile)
    return render(request, "member/loan_apply.html", {"form": form})


@login_required
@member_required
def loan_list(request):
    profile = get_object_or_404(MemberProfile, user=request.user)
    loans = profile.loans.order_by("-created_at")
    return render(request, "member/loan_list.html", {"loans": loans})


@login_required
@member_required
def loan_detail(request, pk):
    loan = get_object_or_404(Loan, pk=pk, member__user=request.user)
    return render(request, "member/loan_detail.html", {"loan": loan})


@login_required
@member_required
def loan_edit(request, pk):
    loan = get_object_or_404(Loan, pk=pk, member__user=request.user, status="PENDING")
    if request.method == "POST":
        form = LoanApplicationForm(request.POST, instance=loan, member=loan.member)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Loan application updated successfully.")
            return redirect("loan_list")
    else:
        form = LoanApplicationForm(instance=loan, member=loan.member)
    return render(request, "member/loan_edit.html", {"form": form, "loan": loan})


@login_required
@member_required
def loan_delete(request, pk):
    loan = get_object_or_404(Loan, pk=pk, member__user=request.user, status="PENDING")
    if request.method == "POST":
        loan.delete()
        messages.success(request, "🗑️ Loan application deleted.")
        return redirect("loan_list")
    return render(request, "member/loan_delete.html", {"loan": loan})



@login_required
@member_required
def repayment_history(request):
    profile = get_object_or_404(MemberProfile, user=request.user)
    repayments = Repayment.objects.filter(loan__member=profile).order_by("-paid_at")
    return render(request, "member/repayment_history.html", {"repayments": repayments})
