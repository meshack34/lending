from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # Auth
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # Admin user creation
    path("admin/create-user/", views.admin_create_user, name="admin_create_user"),
    
#     # Other existing routes
#     path("loans/", views.loan_list, name="loan_list"),
#     path("loans/apply/", views.loan_apply, name="loan_apply"),
]
