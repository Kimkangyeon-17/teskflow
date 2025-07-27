from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = "users"

urlpatterns = [
    # 인증 관련
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("status/", views.auth_status, name="auth_status"),
    # 프로필 관리
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path(
        "password/change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    # 이메일 인증
    path("email/verify/", views.EmailVerificationView.as_view(), name="email_verify"),
    path(
        "email/resend/",
        views.ResendEmailVerificationView.as_view(),
        name="email_resend",
    ),
    # 유틸리티
    path("check-email/", views.check_email_availability, name="check_email"),
    path("delete-account/", views.delete_account, name="delete_account"),
    # 소셜 로그인 (django-allauth)
    path("social/", include("allauth.urls")),
]
