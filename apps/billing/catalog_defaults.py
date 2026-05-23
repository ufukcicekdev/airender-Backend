"""Default plans and credit packs — used by seed_plans and runtime bootstrap."""

from decimal import Decimal

# Internal only — default FK for new users (not shown on pricing).
MEMBER_PLAN = {
    "slug": "member",
    "name": "Pay as you go",
    "description": "Buy credit packs when you need renders. No monthly subscription.",
    "price_monthly": Decimal("0"),
    "price_yearly": Decimal("0"),
    "monthly_description": "",
    "yearly_description": "",
    "credits_monthly": 0,
    "features": [],
    "is_popular": False,
    "sort_order": 0,
}

# No monthly/yearly subscription tiers — credits are sold as one-time packs only.
DEFAULT_PLANS: list[dict] = []

DEFAULT_CREDIT_PACKS = [
    {
        "slug": "credits-100",
        "name": "100 credits",
        "description": "Starter pack — ~12 standard image edits. Best way to begin after signup.",
        "credits": 100,
        "bonus_credits": 0,
        "price": Decimal("4.99"),
        "features": [
            "~$0.05 per credit",
            "Never expires",
            "Stacks with your balance",
        ],
        "is_popular": True,
        "sort_order": 0,
    },
    {
        "slug": "credits-250",
        "name": "250 credits",
        "description": "Mid-size pack for active creators mid-project.",
        "credits": 250,
        "bonus_credits": 0,
        "price": Decimal("10.99"),
        "features": [
            "~$0.044 per credit",
            "Never expires",
            "Stacks with your balance",
        ],
        "is_popular": False,
        "sort_order": 1,
    },
    {
        "slug": "credits-500",
        "name": "500 credits",
        "description": "Best value for studios and heavy render weeks.",
        "credits": 500,
        "bonus_credits": 0,
        "price": Decimal("19.99"),
        "features": [
            "~$0.040 per credit",
            "Never expires",
            "Stacks with your balance",
        ],
        "is_popular": False,
        "sort_order": 2,
    },
]

RETIRED_PLAN_SLUGS = ("free", "pro", "studio")
RETIRED_CREDIT_PACK_SLUGS = ("credits-2000", "credits-10000")
HIDDEN_PLAN_SLUGS = ("member", *RETIRED_PLAN_SLUGS)
