from django.test import SimpleTestCase, override_settings

from apps.rendering.fal_pricing import fal_usd_for_endpoint
from apps.rendering.pricing import RenderPricingParams, usd_to_credits
from types import SimpleNamespace


class FalPricingTests(SimpleTestCase):
    def test_nano_banana_flat(self):
        usd = fal_usd_for_endpoint(
            "fal-ai/nano-banana/edit",
            resolution="4k",
        )
        self.assertAlmostEqual(usd, 0.039)

    def test_veo3_8s_audio(self):
        usd = fal_usd_for_endpoint(
            "fal-ai/veo3/image-to-video",
            duration_seconds=8,
            generate_audio=True,
        )
        self.assertAlmostEqual(usd, 3.2)

    def test_kling_4s(self):
        usd = fal_usd_for_endpoint(
            "fal-ai/kling-video/v1.6/standard/image-to-video",
            duration_seconds=4,
        )
        self.assertAlmostEqual(usd, 0.224)


@override_settings(
    CREDIT_ECONOMICS={
        "USD_PER_CREDIT": 0.06,
        "RENDER_MARGIN_PERCENT": 40,
        "MIN_CREDITS": 1,
    }
)
class CreditConversionTests(SimpleTestCase):
    def test_usd_to_credits_nano(self):
        # $0.039 * 1.4 = 0.0546 / 0.06 → 1 credit
        self.assertEqual(usd_to_credits(0.039), 1)

    def test_estimate_nano_banana_edit(self):
        from apps.rendering.pricing import estimate_render_credits

        model = SimpleNamespace(
            provider="fal",
            credit_cost=3,
            config={"endpoint_path": "fal-ai/nano-banana/edit"},
        )
        credits = estimate_render_credits(
            model,
            category_slug="image-edit",
            render_params=RenderPricingParams(resolution="1k"),
        )
        self.assertEqual(credits, 1)
