import logging
from typing import Dict, List

from ics import Event
from telegram.ext import CallbackContext

from config import EVENTS_URL, EVENTS_MAX_RESULTS, EVENTS_MAX_DAYS, events_enabled
from events import get_events
from i18n import translate, get_user_language
from info_buttons import FileInfoButton, TextInfoButton, InfoButton


def get_welcome_message_after_setting_language(context: CallbackContext) -> str:
    return translate(
        "As a new rebel, you might have some questions. "
        "The Q&A Telegram Channel is really good for that. You should join it 👉 {link} 💬\n\n"
        "However, we've also prepared some information for you to start with.",
        context,
    ).format(link="https://t.me/+ttV6Jfcrpoc5YTE5")


INFO_BUTTONS: Dict[str, InfoButton] = {
    "HEADING_FOR_EXTINCTION_1": FileInfoButton(
        lambda context: translate("Why does XR exist? (the crisis)", context),
        "heading_for_extinction_1.pdf",
        lambda context: translate("Why XR exists.pdf", context),
    ),
    "HEADING_FOR_EXTINCTION_2": FileInfoButton(
        lambda context: translate("What does XR do? (the solution)", context),
        "heading_for_extinction_2.pdf",
        lambda context: translate("What XR does.pdf", context),
    ),
    "XR_STRUCTURES": FileInfoButton(
        lambda context: translate("How is XR organized? (the logistics)", context),
        "xr_structures.pdf",
        lambda context: translate("How XR is organized.pdf", context),
    ),
    "XR_UNOFFICIAL_GUIDE": FileInfoButton(
        lambda context: translate("But really, how does this work? (the reality)", context),
        "xr_unofficial_guide.pdf",
        lambda context: translate("How XR is organized (unofficial guide).pdf", context),
    ),
    "CHATS_OVERVIEW": TextInfoButton(
        lambda context: translate("How do we communicate? (telegram chats)", context),
        lambda context: translate(
            "## TODO ##\nI will send a real nice overview of all Telegram chats here.",
            context,
        ),
    ),
}

if events_enabled():
    INFO_BUTTONS["UPCOMING_EVENTS"] = TextInfoButton(
        lambda context: translate("When do we meet? (upcoming events)", context),
        lambda context: get_events_message(context),
        parse_mode="HTML",
    )


def get_events_message(context: CallbackContext) -> str:
    try:
        events: List[Event] = get_events(EVENTS_URL, EVENTS_MAX_RESULTS, EVENTS_MAX_DAYS)
        if len(events) == 0:
            return translate(
                "As far as I know, there are no upcoming events. "
                "Maybe some of your fellow rebels know more than I do 🙂.",
                context,
            )
        else:
            return translate(
                "These are the upcoming events that I know of:\n\n", context
            ) + "\n\n".join(format_events(events, context))
    except Exception as ex:
        logging.exception("Failed to load upcoming events", exc_info=ex)
        return translate(
            "Oops, something went wrong. I failed to load the upcoming events.", context
        )


def format_events(events: List[Event], context: CallbackContext) -> List[str]:
    language = get_user_language(context)
    formatted_events = []

    for event in events:
        begin = event.begin.format("DD MMMM", locale=language)

        formatted_event = (
            f"{begin}: {event.name}"
            if not event.url
            else f'{begin}: <a href="{event.url}">{event.name}</a>'
        )

        if event.location:
            formatted_event += " @ " + event.location

        formatted_events.append(formatted_event)

    return formatted_events
