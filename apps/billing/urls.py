from django.urls import path

from .views import (
    CreditPackListView,
    MySubscriptionView,
    PlanListView,
    PricingOverviewView,
    PurchaseCreditsView,
    SubscribeView,
)

urlpatterns = [
    path("pricing", PricingOverviewView.as_view(), name="billing-pricing"),
    path("plans", PlanListView.as_view(), name="billing-plans"),
    path("credit-packs", CreditPackListView.as_view(), name="billing-credit-packs"),
    path("subscription", MySubscriptionView.as_view(), name="billing-subscription"),
    path("subscribe", SubscribeView.as_view(), name="billing-subscribe"),
    path("purchase-credits", PurchaseCreditsView.as_view(), name="billing-purchase-credits"),
]
