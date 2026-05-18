from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailVerificationToken, PasswordResetToken, User


def send_verification_email(user: User) -> EmailVerificationToken:
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
    send_mail(
        subject="Verify your Vizmake account",
        message=f"Click to verify: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=not settings.DEBUG,
    )
    return token


def send_password_reset_email(user: User) -> PasswordResetToken:
    PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
    token = PasswordResetToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=1),
    )
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
    send_mail(
        subject="Reset your Vizmake password",
        message=f"Click to reset: {reset_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=not settings.DEBUG,
    )
    return token


def verify_email_token(token_uuid) -> User | None:
    try:
        record = EmailVerificationToken.objects.select_related("user").get(
            token=token_uuid, used=False, expires_at__gt=timezone.now()
        )
    except EmailVerificationToken.DoesNotExist:
        return None
    record.used = True
    record.save(update_fields=["used"])
    user = record.user
    user.is_verified = True
    user.save(update_fields=["is_verified"])
    return user


def reset_password_with_token(token_uuid, new_password) -> bool:
    try:
        record = PasswordResetToken.objects.select_related("user").get(
            token=token_uuid, used=False, expires_at__gt=timezone.now()
        )
    except PasswordResetToken.DoesNotExist:
        return False
    record.used = True
    record.save(update_fields=["used"])
    user = record.user
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True
