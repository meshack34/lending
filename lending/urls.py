# lending/urls.py
from django.urls import path
from .views import admin as admin_views
from .views import manager as manager_views
from .views import auth, member, admin as admin_views, manager as manager_views, officer as officer_views



urlpatterns = [
    # Public
    path("", auth.home, name="home"),

    # Authentication
    path("login/", auth.CustomLoginView.as_view(), name="login"),
    path("logout/", auth.CustomLogoutView.as_view(), name="logout"),
    path("register/", auth.member_register, name="member_register"),

    # Dashboards
    path("dashboard/admin/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/member/", member.member_dashboard, name="member_dashboard"),
    path("dashboard/manager/", manager_views.manager_dashboard, name="manager_dashboard"),
    path("dashboard/officer/", officer_views.officer_dashboard, name="officer_dashboard"),


    
    # -------------------------------
    # Officer URLs
    # -------------------------------
    path("officer/members/", officer_views.member_list, name="officer_member_list"),
    path("officer/loans/", officer_views.loan_list, name="officer_loan_list"),
    path("officer/loans/<int:loan_id>/", officer_views.loan_detail, name="officer_loan_detail"),
    path("officer/repayments/", officer_views.repayment_list, name="officer_repayment_list"),
    path("officer/reports/", officer_views.report_list, name="officer_report_list"),


    # Admin Features - Companies
    path("dashboard/admin/companies/", admin_views.company_list, name="company_list"),
    path("dashboard/admin/companies/create/", admin_views.company_create, name="company_create"),
    path("dashboard/admin/companies/<int:company_id>/edit/", admin_views.company_edit, name="company_edit"),
    path("dashboard/admin/companies/<int:company_id>/delete/", admin_views.company_delete, name="company_delete"),

    # Admin Features - Offices
    path("dashboard/admin/offices/", admin_views.office_list, name="office_list"),
    path("dashboard/admin/offices/create/", admin_views.office_create, name="office_create"),
    path("dashboard/admin/offices/<int:office_id>/edit/", admin_views.office_edit, name="office_edit"),
    path("dashboard/admin/offices/<int:office_id>/delete/", admin_views.office_delete, name="office_delete"),

    # Admin Features - Loan Policies
    path("dashboard/admin/policies/", admin_views.policy_list, name="policy_list"),
    path("dashboard/admin/policies/create/", admin_views.policy_create, name="policy_create"),

    # Admin Features - Reports
    path("dashboard/admin/reports/", admin_views.report_list, name="report_list"),
    path("dashboard/admin/reports/export-members-csv/", admin_views.export_members_csv, name="export_members_csv"),

    # Admin Features - Users
    path("dashboard/admin/users/", admin_views.user_list, name="user_list"),
    path("dashboard/admin/users/create/", admin_views.user_create, name="user_create"),
    path("dashboard/admin/users/<int:user_id>/edit/", admin_views.user_edit, name="user_edit"),
    path("dashboard/admin/users/<int:user_id>/delete/", admin_views.user_delete, name="user_delete"),
    path("dashboard/admin/assign-officers/", admin_views.assign_officers_to_manager, name="assign_officers"),

    # Admin Features - Members
    path("dashboard/admin/members/", admin_views.member_list, name="member_list"),
    path("dashboard/admin/members/create/", admin_views.member_create, name="member_create"),
    path("dashboard/admin/members/<int:member_id>/edit/", admin_views.member_edit, name="member_edit"),
    path("dashboard/admin/members/<int:member_id>/suspend/", admin_views.member_suspend, name="member_suspend"),

    # Member Features
    path("member/profile/", member.member_profile, name="member_profile"),
    path("member/loan/apply/", member.loan_apply, name="loan_apply"),
    path("member/loans/", member.loan_list, name="loan_list"),
    path("member/loans/<int:loan_id>/", member.loan_detail, name="loan_detail"),
    path("member/repayments/", member.repayment_history, name="repayment_history"),
    path('member/loans/<int:pk>/edit/', member.loan_edit, name='loan_edit'),   # <-- make sure this exists
    path('member/loans/<int:pk>/delete/', member.loan_delete, name='loan_delete'),

    path("manager/dashboard/", manager_views.manager_dashboard, name="manager_dashboard"),
    path("manager/officers/", manager_views.officer_list, name="manager_officer_list"),
    path("manager/members/", manager_views.member_list, name="manager_member_list"),
    path("manager/loans/", manager_views.loan_list, name="manager_loan_list"),
    path("manager/loans/<int:loan_id>/", manager_views.loan_detail, name="manager_loan_detail"),
    path("manager/repayments/", manager_views.repayment_list, name="manager_repayment_list"),
    path("manager/reports/", manager_views.report_list, name="manager_report_list"),
    path("manager/export/members/", manager_views.export_members_csv, name="manager_export_members_csv"),
]
