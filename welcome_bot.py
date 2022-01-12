#!/usr/bin/env python

import logging
from typing import Dict

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    PicklePersistence,
    CallbackContext, ChatJoinRequestHandler, CallbackQueryHandler, Filters,
)

from documents import Documents
from secret import API_TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

CHOOSING_LANGUAGE, CHOOSING_INFO = range(2)


def user_joined(update: Update, context: CallbackContext) -> int:
    ask_for_language(update, context)

    context.bot.approve_chat_join_request(update.effective_chat.id, update.effective_user.id)

    return CHOOSING_LANGUAGE


def ask_for_language(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton(text='Nederlands', callback_data='nl'),
         InlineKeyboardButton(text='English', callback_data='en')],
    ]
    markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    welcome_message = "Hi! I'm the XR (Extinction Rebellion) welcome bot. I'm here to show you around. What's your preferred language?\n\n" \
                      "Hoi! Ik ben de XR (Extinction Rebellion) welkomsrobot. Ik ben hier om je op weg te helpen. Welke taal spreek je?"
    context.bot.send_message(update.effective_user.id, welcome_message, reply_markup=markup)

    return CHOOSING_LANGUAGE


def language_selected(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""

    lang = update["callback_query"]["data"]
    update.effective_message.reply_text(f"Great! I will communicate in {lang} with you from now on.")
    context.user_data["language"] = lang

    follow_up_message = "As a new member, you might have some questions. The Q&A Telegram Channel is really good for that. You can join it here: XXX add link\n\n" \
                        "However, we've we've also prepared some information for you to start with."

    buttons = []
    for document in Documents:
        buttons.append([InlineKeyboardButton(text=document.value["description"], callback_data=f"doc_{document.name}")])

    buttons.append([InlineKeyboardButton(text="What are the local communication channels? (telegram chats)",
                                         callback_data="chats")])
    buttons.append([InlineKeyboardButton(text="Thanks, I'm all set. (end this conversation)", callback_data="done")])

    update.effective_message.reply_text(follow_up_message, reply_markup=InlineKeyboardMarkup(buttons))

    return CHOOSING_INFO


def info_requested(update: Update, context: CallbackContext) -> int:
    key = update["callback_query"]["data"]

    if key[0:4] == "doc_":
        doc_key = key[4:]
        try:
            doc = Documents[doc_key].value
            with open(doc["uri"], mode='rb') as file:
                context.bot.send_document(chat_id=update.effective_chat.id, document=file,
                                          filename=f"{doc['description']}.pdf")
        except Exception:
            update.effective_message.reply_text(
                f"Oops, seems like something went wrong. I cannot find or open the document you requested: '{doc_key}'")
    elif key == "chats":
        pass
    elif key == "done":
        update.effective_message.reply_text(
            "Ok then! Feel free to hit me up if you need more info. Just type /start to restart this conversation.")
        return ConversationHandler.END
    else:
        # should never happen
        update.effective_message.reply_text(
            f"Oops, seems like something went wrong: I don't recognize your answer '{key}'")

    update.effective_message.reply_text("Do you want any more information?")

    return CHOOSING_INFO


def fallback_handler(update: Update, context: CallbackContext):
    # TODO: store the message the user sent
    update.effective_message.reply_text(f"I'm not sure how to respond to this. I'm just a simple robot :-(")


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it the bot's token.
    persistence = PicklePersistence(filename='user_data')
    updater = Updater(API_TOKEN, persistence=persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[ChatJoinRequestHandler(user_joined),
                      CommandHandler("start", ask_for_language)],
        states={
            CHOOSING_LANGUAGE: [
                CallbackQueryHandler(language_selected)
            ],
            CHOOSING_INFO: [
                CallbackQueryHandler(info_requested)
            ],
        },
        fallbacks=[MessageHandler(filters=Filters.all, callback=fallback_handler)],
        name="xr_welcome_conversation",
        persistent=True,
    )

    dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
