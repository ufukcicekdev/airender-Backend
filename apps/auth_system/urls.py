from django.urls import path

from .views import (
    CookieTokenRefreshView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationView,
    SignupConfigView,
    VerifyEmailView,
)

urlpatterns = [
    path("signup-config", SignupConfigView.as_view(), name="auth-signup-config"),
    path("register", RegisterView.as_view(), name="auth-register"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
    path("refresh", CookieTokenRefreshView.as_view(), name="auth-refresh"),
    path("me", MeView.as_view(), name="auth-me"),
    path("verify-email", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("password-reset", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("password-reset/confirm", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("resend-verification", ResendVerificationView.as_view(), name="auth-resend-verification"),
]
