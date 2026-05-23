from django.core.management.base import BaseCommand

from apps.auth_system.models import User

DEMO_EMAIL = "demo@flowframe.local"
DEMO_EMAIL_LEGACY = "demo@vizmake.local"
DEMO_PASSWORD = "demo1234"
DEMO_USERNAME = "demo"


class Command(BaseCommand):
    help = f"Create or reset the demo user ({DEMO_EMAIL} / {DEMO_PASSWORD})"

    def handle(self, *args, **options):
        user = (
            User.objects.filter(email=DEMO_EMAIL).first()
            or User.objects.filter(email=DEMO_EMAIL_LEGACY).first()
            or User.objects.filter(username=DEMO_USERNAME).first()
        )

        created = user is None
        if created:
            user = User(email=DEMO_EMAIL, username=DEMO_USERNAME)
        else:
            user.email = DEMO_EMAIL
            user.username = DEMO_USERNAME

        user.set_password(DEMO_PASSWORD)
        user.is_active = True
        user.is_verified = True
        user.credits = 500
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{action} demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        )
