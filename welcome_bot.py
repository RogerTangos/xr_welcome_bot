#!/usr/bin/env python

import gettext
import logging
from functools import wraps

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
    ChatJoinRequestHandler,
    Filters,
)

from documents import Documents
from handlers.privateconversationcallbackqueryhandler import (
    PrivateConversationCallbackQueryHandler,
)
from handlers.privateconversationcommandhandler import PrivateConversationCommandHandler
from handlers.privateconversationmessagehandler import PrivateConversationMessageHandler
from secret import API_TOKEN

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

logger = logging.getLogger(__name__)

CHOOSING_LANGUAGE, CHOOSING_INFO, CHOOSING_MORE_INFO = range(3)

LANG_NL = gettext.translation("nl_NL", localedir="locale", languages=["nl_NL"])

# This is a function that you're going to overwrite,
# but should be explicitly be declared as a function.
# It's possible to do this as a lambda or (the pep-8 preferred way)
# just using def
def translate(text, lang):
    if lang == "nl":
        return LANG_NL.gettext(text)
    else:
        return gettext.gettext(text)


# granted, it's pretty weird to overwrite global functions
# but maybe this how gettext is commonly used? I don't know.


def get_user_language(context: CallbackContext) -> str:
    return context.user_data["language"] if "language" in context.user_data else "en"


def translated(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        lang = get_user_language(context)

        # this is 100% not thread safe and is going to result in the program
        # responding in the wrong language if two different language users are
        # talking to it at the same time.
        # Instead of using update_language, why not set a language attribute
        # in each of the functions? If they default to None, they can still be
        # called with the handler, and then the language can be set in this
        # wrapper. A "translate" function can take the language as a variable.
        # I've gone ahead and implemented that.
        # i.e. def more_info_requested(update: Update, context: CallbackContext, lang=None)

        # update_language(lang)

        result = func(update, context, lang, *args, **kwargs)
        return result

    return wrapped


# def update_language(lang):

#     # this makes me cringe a bit, but aside from making the whole thing OO, I'm not sure how to do it better
#     global translate

#     if lang == "nl":
#         translate = LANG_NL.gettext
#     else:
#         translate = gettext.gettext


def user_joined(update: Update, context: CallbackContext) -> int:
    ask_for_language(update, context)

    context.bot.approve_chat_join_request(update.effective_chat.id, update.effective_user.id)

    # FIXME the state does not seem to be updated after a join request
    return CHOOSING_LANGUAGE


def ask_for_language(update: Update, context: CallbackContext) -> int:
    # TODO: if the update is a join request, and we already have a user context, don't send any message
    #   but return ConversationHandler.END instead
    keyboard = [
        [
            InlineKeyboardButton(text="Nederlands", callback_data="nl"),
            InlineKeyboardButton(text="English", callback_data="en"),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    welcome_message = (
        "Hi! I'm the XR (Extinction Rebellion) welcome bot. "
        "I'm here to show you around. What's your preferred language?\n\n"
        "Hoi! Ik ben de XR (Extinction Rebellion) welkomsrobot. "
        "Ik ben hier om je op weg te helpen. Welke taal spreek je?"
    )
    context.bot.send_message(update.effective_user.id, welcome_message, reply_markup=markup)

    return CHOOSING_LANGUAGE


def language_selected(update: Update, context: CallbackContext) -> int:
    lang = update["callback_query"]["data"]
    update.callback_query.answer()

    if lang != "en" and lang != "nl":
        # ignore invalid button clicks
        return CHOOSING_LANGUAGE

    context.user_data["language"] = lang

    # update_language(lang)

    update.effective_message.reply_text(translate("Great! I will communicate in English with you from now on.", lang))

    send_info_options(update, context)

    return CHOOSING_INFO


@translated
def send_info_options(update: Update, context: CallbackContext, lang=None):
    follow_up_message = translate(
        "As a new member, you might have some questions. "
        "The Q&A Telegram Channel is really good for that. You can join it here: {link}\n\n"
        "However, we've also prepared some information for you to start with.",
        lang,
    ).format(link="{{TODO ADD LINK}}")

    buttons = []
    for document in Documents:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=translate(document.value["description"], lang),
                    callback_data=f"doc_{document.name}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=translate("What are the local communication channels? (telegram chats)", lang),
                callback_data="chats",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=translate("Thanks, I'm all set. (end this conversation)", lang),
                callback_data="done",
            )
        ]
    )

    update.effective_message.reply_text(follow_up_message, reply_markup=InlineKeyboardMarkup(buttons))


@translated
def info_requested(update: Update, context: CallbackContext, lang=None) -> int:
    key = update["callback_query"]["data"]

    if key[0:4] == "doc_":
        doc_key = key[4:]
        try:
            doc = Documents[doc_key].value
            with open(f"files/{get_user_language(context)}/{doc['filename']}", mode="rb") as file:  # TODO i18n
                update.effective_message.reply_text(
                    translate("Please hang on for a second, I'm sending you a file.", lang)
                )

                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file,
                    filename=f"{translate(doc['description'], lang)}.pdf",  # FIXME remove question marks from filenames
                )
        except Exception:
            update.effective_message.reply_text(
                translate(
                    "Oops, seems like something went wrong. I cannot find or open the document you requested: '{doc_key}'.",
                    lang,
                ).format(doc_key=doc_key)
            )
    elif key == "chats":
        # TODO
        update.effective_message.reply_text(
            translate("## TODO ##\nI will send a real nice overview of all Telegram chats here.", lang)
        )
    elif key == "done":
        update.callback_query.answer()
        send_done_message(update, context)
        return ConversationHandler.END
    else:
        # Ignore invalid button clicks
        update.callback_query.answer()
        return CHOOSING_INFO

    update.callback_query.answer()

    buttons = [
        [
            InlineKeyboardButton(text=translate("Yes", lang), callback_data="yes"),
            InlineKeyboardButton(text=translate("No", lang), callback_data="no"),
        ]
    ]

    update.effective_message.reply_text(
        translate("Do you wish to receive any more information?", lang),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

    return CHOOSING_MORE_INFO


@translated
def more_info_requested(update: Update, context: CallbackContext, lang=None) -> int:
    answer = update["callback_query"]["data"]

    update.callback_query.answer()

    if answer == "no":
        send_done_message(update, context)
        return ConversationHandler.END
    elif answer == "yes":
        send_info_options(update, context)
        return CHOOSING_INFO
    else:
        # ignore invalid button clicks
        return CHOOSING_MORE_INFO


@translated
def send_done_message(update: Update, context: CallbackContext, lang=None):
    update.effective_message.reply_text(
        translate(
            "Ok then! Feel free to hit me up if you need more info. Just type /start to restart this conversation.",
            lang=lang,
        )
    )


@translated
def fallback_handler(update: Update, context: CallbackContext, lang=None):
    if update.callback_query is not None:
        # Ignore invalid button clicks
        update.callback_query.answer()
        return

    # TODO: store the message the user sent
    update.effective_message.reply_text(
        translate("I am not sure how to respond to this. I'm just a simple robot :-(", lang)
    )


def main() -> None:
    updater = Updater(API_TOKEN, persistence=PicklePersistence(filename="user_data"))
    dispatcher = updater.dispatcher

    handler = ConversationHandler(
        entry_points=[
            ChatJoinRequestHandler(user_joined),
            PrivateConversationCommandHandler("start", ask_for_language),
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

    dispatcher.add_handler(handler)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
