#!/usr/bin/env python

import logging
from functools import partial
from pathlib import Path

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
    ChatJoinRequestHandler,
    Filters,
)

from content import InfoButtons, get_welcome_message_after_setting_language
from data.secret import API_TOKEN
from src.handlers import (
    PrivateConversationCallbackQueryHandler,
    PrivateConversationCommandHandler,
    PrivateConversationMessageHandler,
)
from src.i18n import translate
from src.info_buttons import FileInfoButton, TextInfoButton, InfoButton

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)

CHOOSING_LANGUAGE, CHOOSING_INFO, CHOOSING_MORE_INFO = range(3)


def start_conversation(update: Update, context: CallbackContext) -> int:
    welcome_message = (
        "Hi! I'm the XR (Extinction Rebellion) chat bot. I'm here to show you around.\n\n"
        "Hoi! Ik ben de XR (Extinction Rebellion) chatbot. Ik ben hier om je op weg te helpen."
    )
    context.bot.send_message(update.effective_user.id, welcome_message)

    ask_for_language(update, context)

    if update.chat_join_request is not None:
        context.bot.approve_chat_join_request(update.effective_chat.id, update.effective_user.id)

    return CHOOSING_LANGUAGE


def ask_for_language(update: Update, context: CallbackContext, set_language_only: bool = False) -> int:
    # TODO: if the update is a join request, and we already have a user context, don't send any message
    #   but return ConversationHandler.END instead
    buttons = [
        [
            InlineKeyboardButton(text="Nederlands", callback_data="nl"),
            InlineKeyboardButton(text="English", callback_data="en"),
        ],
    ]
    context.bot.send_message(update.effective_user.id, "What's your preferred language?\n\nWelke taal spreek je?",
                             reply_markup=InlineKeyboardMarkup(buttons))

    context.user_data["set_language_only"] = set_language_only

    return CHOOSING_LANGUAGE


def language_selected(update: Update, context: CallbackContext) -> int:
    lang = update["callback_query"]["data"]
    update.callback_query.answer()

    if lang != "en" and lang != "nl":
        # ignore invalid button clicks
        return CHOOSING_LANGUAGE

    context.user_data["language"] = lang

    update.effective_message.reply_text(
        translate("Great! I will communicate in English with you from now on.", context)
    )

    end_conversation = context.user_data["set_language_only"] if "set_language_only" in context.user_data else False
    if "set_language_only" in context.user_data:
        del context.user_data["set_language_only"]

    if end_conversation:
        return ConversationHandler.END

    return send_info_options(update, context, include_follow_up_message=True)


def send_info_options(update: Update, context: CallbackContext, include_follow_up_message=False) -> int:
    if include_follow_up_message:
        update.effective_message.reply_text(get_welcome_message_after_setting_language(context))

    info_question = translate("Are you interested in knowing more about any of the following topics?", context)

    buttons = []
    for item in InfoButtons:
        if isinstance(item.value, InfoButton):
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=item.value.get_button_text(context),
                        callback_data=item.name,
                    )
                ]
            )

    buttons.append(
        [
            InlineKeyboardButton(
                text=translate("Thanks, I'm all set. (end this conversation)", context),
                callback_data="__DONE",
            )
        ]
    )

    update.effective_message.reply_text(
        info_question, reply_markup=InlineKeyboardMarkup(buttons)
    )

    return CHOOSING_INFO


def info_requested(update: Update, context: CallbackContext) -> int:
    key = update["callback_query"]["data"]

    try:
        button = InfoButtons[key].value

        if isinstance(button, FileInfoButton):
            try:
                with open(button.get_file_path(context), mode="rb") as file:
                    update.effective_message.reply_text(
                        translate("Just a second, I'm sending you a file.", context)
                    )

                    context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=file,
                        filename=f"{button.get_user_filename(context)}.pdf",
                    )
            except Exception:
                update.effective_message.reply_text(
                    translate(
                        "Oops, seems like something went wrong. "
                        "I cannot find or open the document you requested: '{key}'.",
                        context,
                    ).format(key=key)
                )
        elif isinstance(button, TextInfoButton):
            update.effective_message.reply_text(button.get_info_text(context))
    except KeyError:
        update.callback_query.answer()

        if key == "__DONE":
            send_done_message(update, context)
            return ConversationHandler.END
        else:
            # Ignore invalid button clicks
            return CHOOSING_INFO

    update.callback_query.answer()

    buttons = [
        [
            InlineKeyboardButton(text=translate("Yes", context), callback_data="yes"),
            InlineKeyboardButton(text=translate("No", context), callback_data="no"),
        ]
    ]

    update.effective_message.reply_text(
        translate("Would you like any more information?", context),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

    return CHOOSING_MORE_INFO


def more_info_requested(update: Update, context: CallbackContext) -> int:
    answer = update["callback_query"]["data"]

    update.callback_query.answer()

    if answer == "no":
        send_done_message(update, context)
        return ConversationHandler.END
    elif answer == "yes":
        return send_info_options(update, context)
    else:
        # ignore invalid button clicks
        return CHOOSING_MORE_INFO


def send_done_message(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        translate(
            "Ok then! Feel free to hit me up if you need more info. Just type /info to request information, "
            "/lang to set your preferred language or /start to completely restart this conversation.",
            context,
        )
    )


def fallback_handler(update: Update, context: CallbackContext):
    if update.callback_query is not None:
        # Ignore invalid button clicks
        update.callback_query.answer()
        return

    # TODO: store the message the user sent
    update.effective_message.reply_text(
        translate("I am not sure how to respond to this. I'm just a simple chat bot ☹", context)
    )


def main() -> None:
    updater = Updater(API_TOKEN,
                      persistence=PicklePersistence(filename=str(Path(__file__).parents[1] / "data" / "user_data")))
    dispatcher = updater.dispatcher

    handler = ConversationHandler(
        entry_points=[
            ChatJoinRequestHandler(start_conversation),
            PrivateConversationCommandHandler("start", start_conversation),
            PrivateConversationCommandHandler("lang", partial(ask_for_language, set_language_only=True)),
            PrivateConversationCommandHandler("info", send_info_options)
        ],
        states={
            CHOOSING_LANGUAGE: [PrivateConversationCallbackQueryHandler(language_selected)],
            CHOOSING_INFO: [PrivateConversationCallbackQueryHandler(info_requested)],
            CHOOSING_MORE_INFO: [PrivateConversationCallbackQueryHandler(more_info_requested)],
        },
        fallbacks=[
            PrivateConversationCallbackQueryHandler(fallback_handler),  # this does not seem to work
            PrivateConversationMessageHandler(filters=Filters.all, callback=fallback_handler),
        ],
        name="xr_welcome_conversation",
        persistent=True,
        per_chat=False,
    )

    # TODO add help command
    # TODO add command to reset state / delete user data

    dispatcher.add_handler(handler)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
