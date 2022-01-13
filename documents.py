import enum


# make gettext tools pick up these strings as translations
def _(message):
    return message


class Documents(enum.Enum):
    HEADING_FOR_EXTINCTION_1 = {
        "description": _("Why does XR exist? (the crisis)"),
        "filename": "heading_for_extinction_1.pdf",
    }
    HEADING_FOR_EXTINCTION_2 = {
        "description": _("What does XR do? (the solution)"),
        "filename": "heading_for_extinction_2.pdf",
    }
    XR_STRUCTURES = {
        "description": _("How is XR organized? (the logistics)"),
        "filename": "xr_structures.pdf",
    }
    XR_UNOFFICIAL_GUIDE = {
        "description": _("But really, how does this work? (the reality)"),
        "filename": "xr_unofficial_guide.pdf",
    }


del _
