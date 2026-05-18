"""Prompt presets for Image Edit (inpaint / scene transformation)."""

IMAGE_EDIT_PRESETS = [
    {
        "title": "View to render",
        "icon": "camera",
        "positive": "Create photorealistic image",
        "is_default": True,
    },
    {
        "title": "Add realism",
        "icon": "sparkles",
        "positive": (
            "Make this render photorealistic, add shadows, contrast light, enhance textures"
        ),
    },
    {
        "title": "Night",
        "icon": "moon",
        "positive": (
            "Convert the daytime scene into a moody nighttime shot, bright moon as the primary "
            "light source from window invisible in the scene, soft rim light outlining objects. "
            "Warm interior lights contrasting with cool moonlight tones. Add slight atmospheric "
            "haze or moisture for a cinematic feel. Realistic shadows."
        ),
    },
    {
        "title": "Rain",
        "icon": "cloud-rain",
        "positive": (
            "Change the scene to a rainy day. Overcast sky, soft diffused light, wet surfaces, "
            "realistic rain outside the windows, subtle reflections on the ground, moody "
            "atmosphere, natural lighting, photorealistic render"
        ),
    },
    {
        "title": "Macro closeup",
        "icon": "scan-search",
        "positive": (
            "Extreme macro close-up of a material surface from the scene, revealing fine texture "
            "and realistic imperfections, with surrounding objects softly visible in the "
            "background, cinematic macro photography with shallow depth of field"
        ),
    },
    {
        "title": "Activity closeup",
        "icon": "users",
        "positive": (
            "Close-up of everyday activity within the environment, natural interaction and "
            "cinematic depth of field."
        ),
    },
    {
        "title": "Object closeup",
        "icon": "focus",
        "positive": (
            "Create a beautiful closeup shot showing one of the detail of this image, use depth "
            "of field to blur, add bokeh, show details on focus, add some detailed, small objects"
        ),
    },
    {
        "title": "Animal closeup",
        "icon": "paw-print",
        "positive": (
            "Cinematic close-up of an animal naturally behaving within the environment"
        ),
    },
    {
        "title": "Moodboard",
        "icon": "layout-grid",
        "positive": (
            "Create a high-end interior design material moodboard using only the materials "
            "present in the 3D scene. Arrange the samples in an artistic, layered composition "
            "similar to luxury architectural boards, with realistic textures, shadows, and soft "
            "studio lighting. include stone, wood, fabric, metal, and color swatches exactly as "
            "they appear in the scene, presented as physical material tiles and samples. Use a "
            "neutral background, elegant styling, and balanced composition."
        ),
    },
    {
        "title": "Design board",
        "icon": "layout-template",
        "positive": (
            "Create a high-end editorial design presentation board based on the provided project. "
            "Do not redesign the project - only present it in a premium portfolio style."
        ),
    },
    {
        "title": "Blueprints",
        "icon": "ruler",
        "positive": "Create technical drawings of this object",
    },
    {
        "title": "Axonometry",
        "icon": "box",
        "positive": (
            "Create a 3D cross-section in axonometric orthographic projection, visible from top 3/4"
        ),
    },
    {
        "title": "Clean up",
        "icon": "brush-cleaning",
        "positive": (
            "Transform this image into a clean developer-finish architectural visualization. "
            "Keep original geometry, layout and camera unchanged. Apply smooth painted white "
            "walls, finished floors, clean ceilings, installed windows and doors, neutral modern "
            "materials. Empty, uncluttered space prepared for handover."
        ),
    },
    {
        "title": "Abandoned",
        "icon": "house",
        "positive": (
            "Introduce heavy realistic degradation across the entire scene, including strong dirt "
            "accumulation, stains, cracks, peeling surfaces, worn edges, material damage, "
            "weathering, discoloration, dust and visible aging effects, creating a neglected and "
            "deteriorated environment while maintaining the original layout."
        ),
    },
    {
        "title": "Drone view",
        "icon": "plane",
        "positive": (
            "Move the camera to a high drone viewpoint above the scene, revealing a large "
            "surrounding environment around the project. Keep the main object clearly visible "
            "while preserving original frame proportions and composition"
        ),
    },
    {
        "title": "Unfinished",
        "icon": "hard-hat",
        "positive": (
            "Transform the scene into a realistic unfinished construction state, exposing raw "
            "concrete, structural surfaces and unpainted materials, with visible construction "
            "details such as rough textures, installation elements, exposed areas, dust and "
            "natural building imperfections while maintaining original layout."
        ),
    },
    {
        "title": "Artificial light",
        "icon": "lightbulb",
        "positive": (
            "Change day to night, add LED strips, turn artificial lights on, make cozy vibe"
        ),
    },
    {
        "title": "Night to day",
        "icon": "sunrise",
        "positive": "Change night to day",
    },
    {
        "title": "Golden hour",
        "icon": "sunset",
        "positive": (
            "Change the mood to golden hour, add low, magical sun rays gently piercing through "
            "the shadows"
        ),
    },
    {
        "title": "Make brighter",
        "icon": "sun",
        "positive": "Make a little bit brighter",
    },
    {
        "title": "Add people",
        "icon": "users",
        "positive": "Add people to the image",
    },
    {
        "title": "Blurred people",
        "icon": "person-standing",
        "positive": "Add blurred people in motion",
    },
    {
        "title": "Add cars",
        "icon": "car",
        "positive": "Add cars to the image",
    },
    {
        "title": "Blurred cars",
        "icon": "car-front",
        "positive": "Add blurred cars in motion",
    },
    {
        "title": "Autumn",
        "icon": "leaf",
        "positive": (
            "Ultra-realistic autumn scene with a moody atmosphere, overcast sky, soft diffused "
            "light, light mist in the air, wet ground reflecting subtle light, deep warm browns "
            "and muted orange tones mixed with cool grey shadows, fallen leaves scattered "
            "naturally, damp textures, cinematic mood, realistic fog depth"
        ),
    },
    {
        "title": "Winter",
        "icon": "snowflake",
        "positive": "Transfer this image to winter, add snow",
    },
    {
        "title": "Fog",
        "icon": "cloud-fog",
        "positive": "Add fog",
    },
    {
        "title": "Volumetric",
        "icon": "sun-dim",
        "positive": (
            "Add volumetric rays coming behind trees shadow, enhance atmosphere"
        ),
    },
    {
        "title": "Add birds",
        "icon": "bird",
        "positive": "Add small birds in the sky",
    },
    {
        "title": "Add flowers",
        "icon": "flower-2",
        "positive": "Add flowers",
    },
    {
        "title": "Add grass",
        "icon": "sprout",
        "positive": "Add grass",
    },
    {
        "title": "Add trees",
        "icon": "trees",
        "positive": "Add trees",
    },
    {
        "title": "Logo",
        "icon": "pen-line",
        "positive": "Create a 2d logo of this object",
    },
    {
        "title": "Mockup",
        "icon": "home",
        "positive": (
            "Close-up of an architectural mockup model, axonometry view, depth of field, closeup, "
            "bokeh, highly detailed scale model of this space, clean materials like white foam "
            "board, wood, acrylic, precise miniature windows and structures, placed on a "
            "presentation table, soft studio lighting"
        ),
    },
    {
        "title": "Make sketch",
        "icon": "pencil",
        "positive": "Convert the photo into a pencil sketch",
    },
    {
        "title": "Side view",
        "icon": "move-horizontal",
        "positive": (
            "Move the camera all the way to the right; show objects from a right-side perspective."
        ),
    },
    {
        "title": "Top view",
        "icon": "arrow-down",
        "positive": "Show this space from top",
    },
]
