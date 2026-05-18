import uuid
from decimal import Decimal

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("slug", models.SlugField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True)),
                ("price_monthly", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10)),
                ("price_yearly", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("credits_monthly", models.PositiveIntegerField(default=100)),
                ("features", models.JSONField(default=list)),
                ("is_active", models.BooleanField(default=True)),
                ("is_popular", models.BooleanField(default=False)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "plans", "ordering": ["sort_order", "price_monthly"]},
        ),
        migrations.CreateModel(
            name="UserSubscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("active", "Active"), ("cancelled", "Cancelled"), ("trialing", "Trialing")], default="active", max_length=20)),
                ("billing_cycle", models.CharField(choices=[("monthly", "Monthly"), ("yearly", "Yearly")], default="monthly", max_length=20)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="billing.plan")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="subscription", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "user_subscriptions"},
        ),
    ]
