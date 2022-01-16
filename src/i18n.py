import gettext
from pathlib import Path

from telegram.ext import CallbackContext

LANG_NL = gettext.translation(
    "nl_NL", localedir=Path(__file__).parents[1] / "locale", languages=["nl_NL"]
)


def translate(text: str, context: CallbackContext) -> str:
    lang = get_user_language(context)
    if lang == "nl":
        return LANG_NL.gettext(text)
    else:
        return gettext.gettext(text)


def get_user_language(context: CallbackContext) -> str:
    return context.user_data["language"] if "language" in context.user_data else "en"
