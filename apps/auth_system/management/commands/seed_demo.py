from django.core.management.base import BaseCommand

from apps.auth_system.models import User


class Command(BaseCommand):
    help = "Create or reset the demo user (demo@vizmake.local / demo1234)"

    def handle(self, *args, **options):
        email = "demo@vizmake.local"
        password = "demo1234"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": "demo", "is_verified": True, "credits": 500},
        )
        user.set_password(password)
        user.is_active = True
        user.is_verified = True
        user.credits = 500
        user.username = user.username or "demo"
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} demo user: {email} / {password}"))
