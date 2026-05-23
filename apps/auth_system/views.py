from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
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
    """Expire JWT cookies using the same flags as set_jwt_cookies (delete_cookie lacks httponly)."""
    kw = _cookie_kwargs()
    expired = "Thu, 01 Jan 1970 00:00:00 GMT"
    for name in (settings.JWT_COOKIE_ACCESS, settings.JWT_COOKIE_REFRESH):
        response.set_cookie(
            name,
            "",
            max_age=0,
            expires=expired,
            **kw,
        )
    return response


class SignupConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings = SignupSettings.load()
        return Response(SignupSettingsSerializer(settings).data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not getattr(settings, "ALLOW_PUBLIC_SIGNUP", False):
            return Response(
                {"detail": "Registration is disabled. Contact us for access."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        services.send_verification_email(user)
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        response = Response(
            {
                "user": UserSerializer(user).data,
                "access": access,
                "message": "Registration successful. Check your email.",
            },
            status=status.HTTP_201_CREATED,
        )
        return set_jwt_cookies(response, access, str(refresh))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        response = Response({"user": UserSerializer(user).data, "access": access})
        return set_jwt_cookies(response, access, str(refresh))


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
        refresh = request.COOKIES.get(settings.JWT_COOKIE_REFRESH) or request.data.get(
            "refresh"
        )
        if not refresh:
            resp = Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            return clear_jwt_cookies(resp)

        serializer = self.get_serializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            resp = Response(
                {"detail": "Session expired. Please sign in again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            return clear_jwt_cookies(resp)

        data = serializer.validated_data
        access = str(data["access"])
        # ROTATE_REFRESH_TOKENS blacklists the cookie token; must persist the new refresh.
        new_refresh = str(data.get("refresh") or refresh)
        resp = Response({"message": "Token refreshed.", "access": access})
        return set_jwt_cookies(resp, access, new_refresh)


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
