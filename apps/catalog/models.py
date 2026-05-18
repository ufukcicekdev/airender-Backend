import uuid

from django.db import models


class CapabilityCategory(models.Model):
    """Top-level capability: Image Generate, Image to Video, etc."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=64)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=64,
        default="sparkles",
        help_text="Lucide icon name for the frontend (e.g. image, video, wand-sparkles)",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "capability_categories"
        ordering = ["sort_order", "name"]
        verbose_name_plural = "capability categories"

    def __str__(self):
        return self.name


class CategoryPromptPreset(models.Model):
    """Prompt template tied to a capability category (shown for all models in that category)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        CapabilityCategory,
        on_delete=models.CASCADE,
        related_name="prompt_presets",
    )
    slug = models.SlugField(max_length=64, blank=True)
    title = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, blank=True)
    positive_prompt = models.TextField()
    negative_prompt = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "category_prompt_presets"
        ordering = ["sort_order", "title"]
        unique_together = [("category", "slug")]

    def __str__(self):
        return f"{self.category.name} — {self.title}"


class UserPromptPreset(models.Model):
    """User-saved prompt template scoped to a capability category."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "auth_system.User",
        on_delete=models.CASCADE,
        related_name="prompt_presets",
    )
    category = models.ForeignKey(
        CapabilityCategory,
        on_delete=models.CASCADE,
        related_name="user_prompt_presets",
    )
    title = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, default="sparkles", blank=True)
    positive_prompt = models.TextField()
    negative_prompt = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_prompt_presets"
        ordering = ["sort_order", "-created_at"]
        indexes = [
            models.Index(fields=["user", "category"]),
        ]

    def __str__(self):
        return f"{self.user_id} — {self.category.slug} — {self.title}"


class ModelTag(models.TextChoices):
    FREE = "free", "Free"
    PRO = "pro", "Pro"
    NEW = "new", "New"
    BETA = "beta", "Beta"


class ProviderAdapterKind(models.TextChoices):
    """Maps to rendering.providers registry adapters."""

    FAL = "fal", "Fal queue API"
    COMFY = "comfy", "ComfyUI"
    HTTP = "http", "Generic HTTP (Bearer)"
    STUB = "stub", "Development stub"


class AIProvider(models.Model):
    """
    AI servis tanımı — deploy etmeden Admin'den yeni servis eklenebilir.

    API key değeri DB'de tutulmaz; Railway/.env'de api_key_env_var adıyla okunur.
  """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(
        max_length=64,
        unique=True,
        help_text="AIModel.provider ile aynı (ör. fal, midjourney)",
    )
    name = models.CharField(max_length=128)
    base_url = models.URLField(
        max_length=512,
        blank=True,
        help_text="API base URL (ör. https://queue.fal.run)",
    )
    api_key_env_var = models.CharField(
        max_length=128,
        blank=True,
        help_text="Sunucu .env değişken adı — değer burada değil (ör. FAL_API_KEY)",
    )
    adapter = models.CharField(
        max_length=32,
        choices=ProviderAdapterKind.choices,
        default=ProviderAdapterKind.HTTP,
    )
    default_path = models.CharField(
        max_length=256,
        blank=True,
        help_text="Model config.endpoint_path yoksa kullanılır",
    )
    path_template = models.CharField(
        max_length=256,
        blank=True,
        help_text="Opsiyonel: models/{external_id}/predictions",
    )
    use_external_id_as_path = models.BooleanField(
        default=False,
        help_text="Fal gibi: path = external_id veya config.endpoint_path",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_providers"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def resolve_api_key(self) -> str:
        import os

        if not self.api_key_env_var:
            return ""
        return os.environ.get(self.api_key_env_var, "").strip()


class AIModel(models.Model):
    """Model available under a capability category."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        CapabilityCategory,
        on_delete=models.CASCADE,
        related_name="models",
    )
    slug = models.SlugField(max_length=64)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    tag = models.CharField(
        max_length=16,
        choices=ModelTag.choices,
        blank=True,
        default="",
        help_text="Badge shown in the model picker (Free, Pro, New, …)",
    )
    brand_icon = models.CharField(
        max_length=64,
        blank=True,
        help_text="Brand logo key for the frontend (flux, kling, gpt, …)",
    )
    provider = models.CharField(
        max_length=64,
        blank=True,
        help_text="AIProvider.slug — Admin → AI Providers",
    )
    external_id = models.CharField(
        max_length=256,
        blank=True,
        help_text="Provider model id / Comfy workflow id",
    )
    credit_cost = models.PositiveIntegerField(default=1)
    requires_images = models.BooleanField(
        default=False,
        help_text="Whether this model expects image input(s) before running",
    )
    min_input_images = models.PositiveSmallIntegerField(
        default=0,
        help_text="Minimum images required (0 = optional)",
    )
    max_input_images = models.PositiveSmallIntegerField(
        default=1,
        help_text="Maximum images allowed; 0 = unlimited",
    )
    input_images_label = models.CharField(
        max_length=128,
        blank=True,
        default="Input images",
        help_text="Label shown in the editor sidebar",
    )
    input_images_help = models.TextField(
        blank=True,
        help_text="Hint text under the upload area",
    )
    config = models.JSONField(default=dict, blank=True)
    default_positive = models.TextField(blank=True)
    default_negative = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_models"
        ordering = ["sort_order", "name"]
        unique_together = [("category", "slug")]

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class ModelPromptPreset(models.Model):
    """Prompt template tied to a specific model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(
        AIModel,
        on_delete=models.CASCADE,
        related_name="prompt_presets",
    )
    slug = models.SlugField(max_length=64, blank=True)
    title = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, blank=True)
    positive_prompt = models.TextField()
    negative_prompt = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "model_prompt_presets"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return f"{self.model.name} — {self.title}"
