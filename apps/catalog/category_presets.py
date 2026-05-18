from apps.catalog.image_edit_presets import IMAGE_EDIT_PRESETS
from apps.catalog.video_presets import VIDEO_PRESETS

CATEGORY_PRESETS: dict[str, list[dict]] = {
    "image-generate": [
        {
            "title": "Icon",
            "icon": "pen-line",
            "positive": (
                "Create a minimal UI icon showing: [#DESCRIPTION]. Black line style on white "
                "background, centered composition, ultra minimal vector design, professional "
                "software interface icon, no gradients, no glow."
            ),
            "is_default": True,
        },
        {
            "title": "Model",
            "icon": "person-standing",
            "positive": (
                "A full-body fashion model standing in a clean studio on a pure white background, "
                "highly realistic, professional beauty and fashion photography, elegant pose, "
                "symmetrical body proportions, natural skin texture, soft even studio lighting, "
                "high-end editorial look"
            ),
        },
        {
            "title": "Futuristic arch",
            "icon": "box",
            "positive": (
                "Conceptual architecture of a futuristic cultural center with fluid parametric "
                "forms, sweeping curves, dynamic asymmetry, sculptural volumes, seamless white "
                "surfaces, glass and steel facade, dramatic cantilevers, photorealistic "
                "architectural visualization, soft daylight"
            ),
        },
        {
            "title": "Concept car",
            "icon": "car",
            "positive": (
                "Futuristic sports car concept, form exploration, automotive design development "
                "sketch, searching for shape, low and elongated proportions, aggressive and "
                "aerodynamic silhouette, bold side cut, smooth canopy, studio lighting, reflective "
                "surfaces, design presentation render"
            ),
        },
        {
            "title": "Enhance realism",
            "icon": "sparkles",
            "positive": "ultra photorealistic, 8k detail, cinematic lighting, sharp focus",
            "negative": "cartoon, illustration, blurry",
        },
        {
            "title": "Studio render",
            "icon": "sparkles",
            "positive": "architectural visualization, clean studio light, 8k",
        },
        {
            "title": "Concept viz",
            "icon": "sparkles",
            "positive": "early concept render, soft lighting, design intent clear",
        },
        {
            "title": "Volumetric rays",
            "icon": "sun",
            "positive": "god rays through windows, volumetric light, dusty atmosphere",
            "negative": "flat lighting",
        },
        {
            "title": "Winter scene",
            "icon": "snowflake",
            "positive": "snow covered landscape, cold winter mood, soft blue hour light",
            "negative": "summer, green leaves",
        },
        {
            "title": "Axonometry",
            "icon": "ruler",
            "positive": "axonometric view, technical illustration style, white background",
            "negative": "perspective distortion",
        },
        {
            "title": "Technical drawing",
            "icon": "pen-line",
            "positive": "architectural line drawing, blueprint style, precise linework",
            "negative": "photo, color fill",
        },
    ],
    "image-to-video": VIDEO_PRESETS,
    "image-edit": IMAGE_EDIT_PRESETS,
    "3d-model": [
        {
            "title": "Architectural prop",
            "icon": "sparkles",
            "positive": "furniture or decor object, watertight mesh, realistic materials",
            "is_default": True,
        },
        {
            "title": "From photo",
            "icon": "image",
            "positive": "match reference silhouette, quad-friendly topology",
            "negative": "broken mesh, floating geometry",
        },
    ],
    "upscale": [
        {
            "title": "AI enhance",
            "icon": "sparkles",
            "positive": "enhance micro detail, sharpen edges, remove noise",
            "is_default": True,
        },
    ],
}
