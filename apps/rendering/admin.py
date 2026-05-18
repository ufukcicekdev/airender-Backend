from django.contrib import admin

from .models import GeneratedImage, RenderTask


@admin.register(RenderTask)
class RenderTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "progress", "created_at")


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ("id", "render_task", "created_at")
