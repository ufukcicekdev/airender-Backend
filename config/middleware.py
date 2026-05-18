"""Middleware — health checks bypass host validation (Railway probes)."""

from django.http import JsonResponse

_HEALTH_PATHS = frozenset({"/health", "/health/", "/api/health", "/api/health/"})


class HealthCheckMiddleware:
    """Respond to health probes before ALLOWED_HOSTS / full Django stack issues."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in _HEALTH_PATHS:
            return JsonResponse({"status": "ok"})
        return self.get_response(request)
