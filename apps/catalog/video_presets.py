"""Prompt presets for Video Creator (image-to-video)."""

VIDEO_PRESETS = [
    {
        "title": "Rotate",
        "icon": "rotate-3d",
        "positive": "Perform a rotational camera move",
        "is_default": True,
    },
    {
        "title": "Drone rise",
        "icon": "plane",
        "positive": (
            "Fast upward drone movement staying centered on the subject, revealing "
            "large-scale environment and expansive surroundings, cinematic aerial motion"
        ),
    },
    {
        "title": "Zoom in",
        "icon": "zoom-in",
        "positive": "Move forward",
    },
    {
        "title": "Zoom out",
        "icon": "zoom-out",
        "positive": "Move backward",
    },
    {
        "title": "DOF close up",
        "icon": "focus",
        "positive": (
            "Slow cinematic camera movement with very shallow depth of field and smooth "
            "focus pull, gradually shifting focus between foreground and background with "
            "strong realistic lens bokeh"
        ),
    },
    {
        "title": "People timelapse",
        "icon": "clock",
        "positive": (
            "Fast timelapse movie. People are walking around this space and having fun. "
            "Add camera movement"
        ),
    },
    {
        "title": "People walking",
        "icon": "users",
        "positive": (
            "A few people are casually moving through the space, interacting naturally and "
            "enjoying their surroundings. Subtle camera movement enhances the sense of "
            "realism and liveliness"
        ),
    },
    {
        "title": "Cute animal",
        "icon": "paw-print",
        "positive": (
            "Add a small, cute animal moving gently through the environment, bringing a "
            "lively and charming touch to the scene."
        ),
    },
]
