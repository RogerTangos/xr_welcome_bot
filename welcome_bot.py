# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to handle chat join requests.
Greets new users with a private message & automatically accepts them into the chat.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import List

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, ChatJoinRequestHandler, CallbackQueryHandler

from documents import Documents
from secret import API_TOKEN

with open("welcome_text.txt") as f:
    WELCOME_TEXT = f.read()
WELCOME_BOT = Bot(API_TOKEN)

# Enable logging
logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def respond_to_button_click(update: Update, context: CallbackContext):
    logger.info("Responding to button click")

    query = update.callback_query

    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def send_welcome_messages(user_id) -> List:
    logger.info(f"Sending welcome messages to user_id {user_id}")

    buttons = []
    for document in Documents:
        buttons.append([InlineKeyboardButton(text=document.value["description"], callback_data=document.name)])
    #
    # buttons = [list(InlineKeyboardButton(text=document.value["description"], callback_data=document.name)) for document
    #            in
    #            Documents]

    custom_keyboard_markup = InlineKeyboardMarkup(
        buttons
    )

    first_message = WELCOME_BOT.send_message(user_id, WELCOME_TEXT)
    second_message = WELCOME_BOT.send_message(
        text="Please choose:",
        chat_id=first_message.chat.id,
        reply_markup=custom_keyboard_markup,
    )
    return [first_message, second_message]


def approve_new_member(effective_chat_id, user_id) -> bool:
    logger.info(f"Approving join request from user_id {user_id}")

    return WELCOME_BOT.approve_chat_join_request(effective_chat_id, user_id)


def initiate_welcome_for_new_members(update: Update, context: CallbackContext) -> None:
    user_id = update.to_dict()["chat_join_request"]["from"]["id"]
    messages = send_welcome_messages(user_id)
    approved = approve_new_member(update.effective_chat.id, user_id)


# def button(update: Update, context: CallbackContext) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     query.answer()

#     query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Handle members requesting to join a chat
    dispatcher.add_handler(ChatJoinRequestHandler(initiate_welcome_for_new_members))
    dispatcher.add_handler(CallbackQueryHandler(respond_to_button_click))

    # Start the Bot
    updater.start_polling(allowed_updates=[Update.CHAT_JOIN_REQUEST, Update.CALLBACK_QUERY])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()