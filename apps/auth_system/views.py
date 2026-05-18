from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from . import services
from .models import SignupSettings, User
from .serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    SignupSettingsSerializer,
    UserSerializer,
)


def _cookie_kwargs():
    return {
        "httponly": settings.JWT_COOKIE_HTTPONLY,
        "secure": settings.JWT_COOKIE_SECURE,
        "samesite": settings.JWT_COOKIE_SAMESITE,
        "path": getattr(settings, "JWT_COOKIE_PATH", "/"),
    }


def set_jwt_cookies(response: Response, access: str, refresh: str) -> Response:
    kw = _cookie_kwargs()
    response.set_cookie(
        settings.JWT_COOKIE_ACCESS,
        access,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        **kw,
    )
    response.set_cookie(
        settings.JWT_COOKIE_REFRESH,
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        **kw,
    )
    return response


def clear_jwt_cookies(response: Response) -> Response:
    kw = _cookie_kwargs()
    response.delete_cookie(settings.JWT_COOKIE_ACCESS, **kw)
    response.delete_cookie(settings.JWT_COOKIE_REFRESH, **kw)
    return response


class SignupConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings = SignupSettings.load()
        return Response(SignupSettingsSerializer(settings).data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        services.send_verification_email(user)
        refresh = RefreshToken.for_user(user)
        response = Response(
            {"user": UserSerializer(user).data, "message": "Registration successful. Check your email."},
            status=status.HTTP_201_CREATED,
        )
        return set_jwt_cookies(response, str(refresh.access_token), str(refresh))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response = Response({"user": UserSerializer(user).data})
        return set_jwt_cookies(response, str(refresh.access_token), str(refresh))


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_COOKIE_REFRESH) or request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        response = Response({"message": "Logged out."})
        return clear_jwt_cookies(response)


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(settings.JWT_COOKIE_REFRESH) or request.data.get("refresh")
        serializer = self.get_serializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        resp = Response({"message": "Token refreshed."})
        return set_jwt_cookies(resp, str(data["access"]), refresh)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        user = services.verify_email_token(token)
        if not user:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"user": UserSerializer(user).data, "message": "Email verified."})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data["email"])
            services.send_password_reset_email(user)
        except User.DoesNotExist:
            pass
        return Response({"message": "If the email exists, a reset link was sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ok = services.reset_password_with_token(
            serializer.validated_data["token"],
            serializer.validated_data["password"],
        )
        if not ok:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Password updated."})


class ResendVerificationView(APIView):
    def post(self, request):
        if request.user.is_verified:
            return Response({"message": "Already verified."})
        services.send_verification_email(request.user)
        return Response({"message": "Verification email sent."})
