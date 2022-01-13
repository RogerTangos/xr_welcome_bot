#!/usr/bin/env python

import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
    Filters,
)

from documents import Documents
from secret import API_TOKEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)

CHOOSING_LANGUAGE, CHOOSING_INFO, CHOOSING_MORE_INFO = range(3)


def user_joined(update: Update, context: CallbackContext) -> int:
    ask_for_language(update, context)

    context.bot.approve_chat_join_request(
        update.effective_chat.id, update.effective_user.id
    )

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
    context.bot.send_message(
        update.effective_user.id, welcome_message, reply_markup=markup
    )

    return CHOOSING_LANGUAGE


def language_selected(update: Update, context: CallbackContext) -> int:
    lang = update["callback_query"]["data"]
    update.callback_query.answer()

    if lang != "en" and lang != "nl":
        # ignore invalid button clicks
        return CHOOSING_LANGUAGE

    update.effective_message.reply_text(
        f"Great! I will communicate in {lang} with you from now on."
    )
    context.user_data["language"] = lang

    send_info_options(update, context)

    return CHOOSING_INFO


def send_info_options(update: Update, context: CallbackContext):
    follow_up_message = (
        "As a new member, you might have some questions. "
        "The Q&A Telegram Channel is really good for that. You can join it here: XXX add link\n\n"
        "However, we've we've also prepared some information for you to start with."
    )

    buttons = []
    for document in Documents:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=document.value["description"],
                    callback_data=f"doc_{document.name}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="What are the local communication channels? (telegram chats)",
                callback_data="chats",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Thanks, I'm all set. (end this conversation)",
                callback_data="done",
            )
        ]
    )

    update.effective_message.reply_text(
        follow_up_message, reply_markup=InlineKeyboardMarkup(buttons)
    )


def info_requested(update: Update, context: CallbackContext) -> int:
    key = update["callback_query"]["data"]

    if key[0:4] == "doc_":
        doc_key = key[4:]
        try:
            doc = Documents[doc_key].value
            with open(f"files/en/{doc['filename']}", mode="rb") as file:  # TODO i18n
                update.effective_message.reply_text(
                    "Please hang on for a second, I'm sending you a file"
                )

                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file,
                    filename=f"{doc['description']}.pdf",  # FIXME remove question marks from filenames
                )
        except Exception:
            update.effective_message.reply_text(
                f"Oops, seems like something went wrong. I cannot find or open the document you requested: '{doc_key}'"
            )
    elif key == "chats":
        # TODO
        update.effective_message.reply_text(
            "## TODO ##\nI will send a real nice overview of all Telegram chats here"
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
            InlineKeyboardButton(text="Yes", callback_data="yes"),
            InlineKeyboardButton(text="No", callback_data="no"),
        ]
    ]

    update.effective_message.reply_text(
        "Do you wish to receive any more information?", reply_markup=InlineKeyboardMarkup(buttons)
    )

    return CHOOSING_MORE_INFO


def more_info_requested(update: Update, context: CallbackContext) -> int:
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


def send_done_message(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Ok then! Feel free to hit me up if you need more info. Just type /start to restart this conversation."
    )


def fallback_handler(update: Update, context: CallbackContext):
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        # Ignore any messages except private messages
        return

    if update.callback_query is not None:
        # Ignore invalid button clicks
        update.callback_query.answer()
        return

    # TODO: store the message the user sent
    update.effective_message.reply_text(
        f"I'm not sure how to respond to this. I'm just a simple robot :-("
    )


def main() -> None:
    updater = Updater(API_TOKEN, persistence=PicklePersistence(filename="user_data"))
    dispatcher = updater.dispatcher

    handler = ConversationHandler(
        entry_points=[
            ChatJoinRequestHandler(user_joined),
            CommandHandler("start", ask_for_language),
        ],
        states={
            CHOOSING_LANGUAGE: [CallbackQueryHandler(language_selected)],
            CHOOSING_INFO: [CallbackQueryHandler(info_requested)],
            CHOOSING_MORE_INFO: [CallbackQueryHandler(more_info_requested)],
        },
        fallbacks=[
            CallbackQueryHandler(fallback_handler),  # this does not seem to work
            MessageHandler(filters=Filters.all, callback=fallback_handler),
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
