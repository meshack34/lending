from django.urls import path
from .views import auth, dashboards, member

urlpatterns = [
    # Public
    path("", auth.home, name="home"),

    # Authentication
    path("login/", auth.CustomLoginView.as_view(), name="login"),
    path("logout/", auth.CustomLogoutView.as_view(), name="logout"),
    path("register/", auth.member_register, name="member_register"),

    # Dashboards
    path("dashboard/admin/", dashboards.admin_dashboard, name="admin_dashboard"),
    path("dashboard/manager/", dashboards.manager_dashboard, name="manager_dashboard"),
    path("dashboard/officer/", dashboards.officer_dashboard, name="officer_dashboard"),
    path("dashboard/member/", member.member_dashboard, name="member_dashboard"),

    # Member features
    path("member/profile/", member.member_profile, name="member_profile"),
    path("member/loan/apply/", member.loan_apply, name="loan_apply"),
    path("member/loans/", member.loan_list, name="loan_list"),
    path("member/loans/<int:loan_id>/", member.loan_detail, name="loan_detail"),
    path("member/repayments/", member.repayment_history, name="repayment_history"),
]
