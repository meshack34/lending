from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from .forms import CustomLoginForm, MemberRegistrationForm

User = get_user_model()


def home(request):
    return render(request, "lending/home.html")


# -------------------------------
# Authentication Views
# -------------------------------
class CustomLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomLoginForm

    def get_success_url(self):
        """Redirect user to role-based dashboard."""
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


# -------------------------------
# Registration (Members only)
# -------------------------------
def member_register(request):
    if request.user.is_authenticated:
        return redirect("login")  # prevent logged-in users from re-registering

    if request.method == "POST":
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            messages.success(request, "Account created successfully.")
            return redirect("member_dashboard")
    else:
        form = MemberRegistrationForm()

    return render(request, "auth/register_member.html", {"form": form})


# -------------------------------
# Role Checks (Authorization)
# -------------------------------
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_admin())(view_func)

def manager_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_manager())(view_func)

def officer_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_officer())(view_func)

def member_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_member())(view_func)
# -------------------------------


# -------------------------------
# Dashboards (Restricted)
# -------------------------------
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



from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from .forms import (
    CustomLoginForm,
    MemberRegistrationForm,
    MemberProfileForm,
    LoanApplicationForm,
)
from .models import Loan, Repayment, MemberProfile

User = get_user_model()



# -------------------------------
# Member Dashboard
# -------------------------------

from django.db.models.functions import TruncMonth
from django.db.models import Sum

@login_required
@member_required
def member_dashboard(request):
    """Member overview: profile, loans, repayment summary, and analytics."""
    profile = getattr(request.user, "profile", None)

    # All loans belonging to this member
    loans = Loan.objects.filter(member=profile).order_by("-created_at")
    active_loans = loans.filter(status__in=["PENDING", "APPROVED", "DISBURSED"])
    closed_loans = loans.filter(status="CLOSED")

    # Repayments
    repayments = Repayment.objects.filter(loan__member=profile).order_by("-paid_at")
    recent_repayments = repayments[:5]

    # --- Analytics ---
    total_loans = loans.count()
    total_principal = loans.aggregate(total=Sum("principal_amount"))["total"] or 0
    total_repaid = repayments.aggregate(total=Sum("amount"))["total"] or 0
    outstanding_balance = max(total_principal - total_repaid, 0)

    # Monthly repayment trend (last 6 months)
    repayment_trend = (
        repayments.annotate(month=TruncMonth("paid_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    context = {
        "profile": profile,
        "active_loans": active_loans,
        "closed_loans": closed_loans,
        "recent_repayments": recent_repayments,
        "total_loans": total_loans,
        "total_principal": total_principal,
        "total_repaid": total_repaid,
        "outstanding_balance": outstanding_balance,
        "repayment_trend": repayment_trend,
    }
    return render(request, "dashboard/member.html", context)


# @login_required
# @member_required
# def member_dashboard(request):
#     """Member overview: profile, loans, repayment summary, and analytics."""
#     profile = getattr(request.user, "profile", None)

#     loans = Loan.objects.filter(member=profile).order_by("-created_at")
#     active_loans = loans.filter(status__in=["PENDING", "APPROVED", "DISBURSED"])
#     closed_loans = loans.filter(status="CLOSED")

#     repayments = Repayment.objects.filter(loan__member=profile).order_by("-paid_at")
#     recent_repayments = repayments[:5]

#     # Analytics
#     total_loans = loans.count()
#     total_principal = sum(l.principal_amount for l in loans)
#     total_repaid = sum(r.amount for r in repayments)
#     outstanding_balance = total_principal - total_repaid

#     # Monthly repayments trend (last 6 months)
#     from django.db.models.functions import TruncMonth
#     from django.db.models import Sum
#     repayment_trend = (
#         repayments.annotate(month=TruncMonth("paid_at"))
#         .values("month")
#         .annotate(total=Sum("amount"))
#         .order_by("month")
#     )

#     context = {
#         "profile": profile,
#         "active_loans": active_loans,
#         "closed_loans": closed_loans,
#         "recent_repayments": recent_repayments,
#         "total_loans": total_loans,
#         "total_principal": total_principal,
#         "total_repaid": total_repaid,
#         "outstanding_balance": outstanding_balance,
#         "repayment_trend": repayment_trend,
#     }
#     return render(request, "dashboard/member.html", context)


# @login_required
# @member_required
# def member_dashboard(request):
#     """Member overview: profile, active loan, repayment summary."""
#     profile = getattr(request.user, "profile", None)
#     active_loans = Loan.objects.filter(member=profile, status__in=["PENDING", "APPROVED", "DISBURSED"])
#     repayments = Repayment.objects.filter(loan__member=profile).order_by("-paid_at")[:5]

#     context = {
#         "profile": profile,
#         "active_loans": active_loans,
#         "recent_repayments": repayments,
#     }
#     return render(request, "dashboard/member.html", context)


# -------------------------------
# Member Profile Management
# -------------------------------
@login_required
@member_required
def member_profile(request):
    """Allow member to update personal details (except ID)."""
    profile = get_object_or_404(MemberProfile, user=request.user)

    if request.method == "POST":
        form = MemberProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("member_profile")
    else:
        form = MemberProfileForm(instance=profile)

    return render(request, "member/profile.html", {"form": form})


# -------------------------------
# Loan Application
# -------------------------------
@login_required
@member_required
def loan_apply(request):
    """Allow member to apply for a new loan."""
    profile = get_object_or_404(MemberProfile, user=request.user)

    if request.method == "POST":
        form = LoanApplicationForm(request.POST, member=profile)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = profile
            loan.interest_rate = loan.policy.interest_rate  # snapshot
            loan.save()
            messages.success(request, "Loan application submitted successfully.")
            return redirect("loan_list")
    else:
        form = LoanApplicationForm(member=profile)

    return render(request, "member/loan_apply.html", {"form": form})


# -------------------------------
# Loan List
# -------------------------------
@login_required
@member_required
def loan_list(request):
    """Show all loans of the logged-in member."""
    profile = get_object_or_404(MemberProfile, user=request.user)
    loans = Loan.objects.filter(member=profile).order_by("-created_at")
    return render(request, "member/loan_list.html", {"loans": loans})


# -------------------------------
# Loan Detail + Repayment History
# -------------------------------
@login_required
@member_required
def loan_detail(request, loan_id):
    """Detailed view of a loan and its repayments."""
    profile = get_object_or_404(MemberProfile, user=request.user)
    loan = get_object_or_404(Loan, id=loan_id, member=profile)
    repayments = loan.repayments.all().order_by("-paid_at")

    return render(request, "member/loan_detail.html", {
        "loan": loan,
        "repayments": repayments,
    })


# -------------------------------
# Repayment History (all loans)
# -------------------------------
@login_required
@member_required
def repayment_history(request):
    """List of all repayments made by this member."""
    profile = get_object_or_404(MemberProfile, user=request.user)
    repayments = Repayment.objects.filter(loan__member=profile).order_by("-paid_at")

    return render(request, "member/repayment_history.html", {"repayments": repayments})
