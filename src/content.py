import enum

from telegram.ext import CallbackContext

from i18n import translate
from info_buttons import FileInfoButton, TextInfoButton
from telegram_orientation import group_listing


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
        lambda context: translate("But really, how does this work? (the reality)", context),
        "xr_unofficial_guide.pdf",
        lambda context: translate("How XR is organized (unofficial guide).pdf", context),
    )
    CHATS_OVERVIEW = TextInfoButton(
        lambda context: translate("How do we communicate? (telegram chats)", context),
        lambda context: translate(
            """1. Broadcast XR Arnhem/Nijmegen: meant to share upcoming actions, training sessions or urgent requests. Anyone is allowed to post something, but check with yourself whether it is meant to be in this channel. Follow this channel if you want to keep updated on what is going on with XR Arnhem/Nijmegen: https://t.me/+sYv9G_Vj7242OGY8\n\n
2. Dorpsplein XR Arnhem/Nijmegen: This chat is meant for discussing actions and XR related questions. We advise to not have eleborated discussions, if you want to do this you can dm eachother or add an agenda point to the next meeting. Follow this channel if you want to be more involved and active in XR Arnhem/Nijmegen: https://t.me/+8XoE2kNOp0FkMTNk\n\n
3. Information Share XR Arnhem/Nijmegen: This chat is meant to share information, news articles and petitions about anything related to climate. Follow this channel if you are interested in keeping updated about the latest news about the climate and the environment: https://t.me/+iy7GRiokIoFkN2E8\n\n
4. Welcome XR Arnhem/Nijmegen: This chat is meant for new rebels who have questions about our local group. Contact @mrpimmetjepom if you want to join this group or for questions. https://t.me/+ttV6Jfcrpoc5YTE5\n\n
5. Arts XR Arnhem/Nijmegen: This chat is meant for people that want to join the Arts circle. This circle creates different artworks for actions or other XR related events. Contact @boktor if you want to join this circle or for questions.\n\n
6. Onboarding and Integration XR Arnhem/Nijmegen: This chat is meant for people that want to join the Onboarding and Integration circle. This circle provides an integration programme for new rebels. https://t.me/+YThz2Az4xdFiZTg5\n\n
7. There are different Affinity Groups, if you have any questions about them or if you want to join one or have any questions, you can contact @pepijnv.\n\n
8. There are different working groups, that are focused on specific actions or longterm projects. Ask around on dorpsplein if you want to join any of them.""",
            context,
        ),
    )

    @classmethod
    def string_in_buttons(cls, mystring: str) -> bool:
        for button in InfoButtons:
            if button.name == mystring:
                return True
        return False
