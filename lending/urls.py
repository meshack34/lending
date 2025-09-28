from django.urls import path
from . import views
from .views import (
    CustomLoginView, CustomLogoutView,
    member_register,
    admin_dashboard, manager_dashboard, officer_dashboard, member_dashboard,
    member_profile, loan_apply, loan_list, loan_detail, repayment_history,
)

urlpatterns = [
    # Public
    path("", views.home, name="home"),

    # Authentication
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", member_register, name="member_register"),

    # Dashboards
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/manager/", manager_dashboard, name="manager_dashboard"),
    path("dashboard/officer/", officer_dashboard, name="officer_dashboard"),
    path("dashboard/member/", member_dashboard, name="member_dashboard"),

    # Member features
    path("member/profile/", member_profile, name="member_profile"),
    path("member/loan/apply/", loan_apply, name="loan_apply"),
    path("member/loans/", loan_list, name="loan_list"),
    path("member/loans/<int:loan_id>/", loan_detail, name="loan_detail"),
    path("member/repayments/", repayment_history, name="repayment_history"),
]
