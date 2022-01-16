import enum

from telegram.ext import CallbackContext

from i18n import translate
from info_buttons import FileInfoButton, TextInfoButton


def get_welcome_message_after_setting_language(context: CallbackContext) -> str:
    return translate(
        "As a new rebel, you might have some questions. "
        "The Q&A Telegram Channel is really good for that. You should join it 👉 {link} 💬\n\n"
        "However, we've also prepared some information for you to start with.",
        context,
    ).format(link="https://t.me/+ttV6Jfcrpoc5YTE5")


class InfoButtons(enum.Enum):
    HEADING_FOR_EXTINCTION_1 = FileInfoButton(
        lambda context: translate("Why does XR exist? (the crisis)", context),
        "heading_for_extinction_1.pdf",
        lambda context: translate("Why XR exists.pdf", context),
    )
    HEADING_FOR_EXTINCTION_2 = FileInfoButton(
        lambda context: translate("What does XR do? (the solution)", context),
        "heading_for_extinction_2.pdf",
        lambda context: translate("What XR does.pdf", context),
    )
    XR_STRUCTURES = FileInfoButton(
        lambda context: translate("How is XR organized? (the logistics)", context),
        "xr_structures.pdf",
        lambda context: translate("How XR is organized.pdf", context),
    )
    XR_UNOFFICIAL_GUIDE = FileInfoButton(
        lambda context: translate(
            "But really, how does this work? (the reality)", context
        ),
        "xr_unofficial_guide.pdf",
        lambda context: translate(
            "How XR is organized (unofficial guide).pdf", context
        ),
    )
    CHATS_OVERVIEW = TextInfoButton(
        lambda context: translate("How do we communicate? (telegram chats)", context),
        lambda context: translate(
            "## TODO ##\nI will send a real nice overview of all Telegram chats here.",
            context,
        ),
    )
