from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CreditPack, Plan
from .serializers import (
    CreditPackSerializer,
    PlanSerializer,
    PricingOverviewSerializer,
    PurchaseCreditsSerializer,
    SubscribeSerializer,
    UserSubscriptionSerializer,
)
from .services import (
    ensure_user_subscription,
    get_pricing_overview,
    purchase_credit_pack,
    subscribe_user,
)


class PricingOverviewView(APIView):
    """Plans, credit packs, and pricing page copy (public)."""

    permission_classes = [AllowAny]

    def get(self, request):
        data = get_pricing_overview()
        return Response(
            PricingOverviewSerializer(
                {
                    "settings": data["settings"],
                    "plans": data["plans"],
                    "credit_packs": data["credit_packs"],
                }
            ).data
        )


class PlanListView(APIView):
    """Public list of active plans (backward compatible)."""

    permission_classes = [AllowAny]

    def get(self, request):
        plans = Plan.objects.filter(is_active=True)
        return Response(PlanSerializer(plans, many=True).data)


class CreditPackListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        packs = CreditPack.objects.filter(is_active=True)
        return Response(CreditPackSerializer(packs, many=True).data)


class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sub = ensure_user_subscription(request.user)
        return Response(UserSubscriptionSerializer(sub).data)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            sub = subscribe_user(
                request.user,
                serializer.validated_data["plan_slug"],
                serializer.validated_data["billing_cycle"],
            )
        except Plan.DoesNotExist:
            return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSubscriptionSerializer(sub).data)


class PurchaseCreditsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PurchaseCreditsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pack = purchase_credit_pack(request.user, serializer.validated_data["pack_slug"])
        except CreditPack.DoesNotExist:
            return Response({"error": "Credit pack not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "pack": CreditPackSerializer(pack).data,
                "credits_added": pack.total_credits,
                "credits_balance": request.user.credits,
            }
        )
