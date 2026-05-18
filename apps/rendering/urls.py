from django.urls import path

from .views import (
    CancelRenderView,
    RenderHistoryView,
    RenderPreviewView,
    RenderStatusView,
    StartRenderView,
)

urlpatterns = [
    path("start", StartRenderView.as_view(), name="render-start"),
    path("history", RenderHistoryView.as_view(), name="render-history"),
    path(
        "<uuid:task_id>/preview",
        RenderPreviewView.as_view(),
        name="render-preview",
    ),
    path("<uuid:task_id>", RenderStatusView.as_view(), name="render-status"),
    path("<uuid:task_id>/cancel", CancelRenderView.as_view(), name="render-cancel"),
]
