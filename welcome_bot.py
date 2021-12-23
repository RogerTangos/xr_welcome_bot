# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to handle chat join requests.
Greets new users with a private message & automatically accepts them into the chat.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from secret import API_TOKEN

from telegram import Update, Bot, Contact
from telegram.ext import (
    Updater,
    CallbackContext,
    ChatJoinRequestHandler,
)

# Enable logging
logging.basicConfig(
    format="%(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# This is a global var and is bad practice
with open('welcome_text.txt') as f:
    welcome_text = f.read()


def welcome_new_members(update: Update, context: CallbackContext) -> None:
    user_id = update.to_dict()['chat_join_request']['from']['id']
    bot = Bot(API_TOKEN)
    message = bot.send_message(user_id, welcome_text)
    contact = Contact(phone_number='123456', first_name='Contact', user_id=user_id)
    # import pdb; pdb.set_trace()
    # bot.send_contact(chat_id=message.chat.id, contact=contact)
    # with open('Moomin.tgs', 'rb') as f:
    #     bot.send_sticker(update.effective_chat.id, user_id, f)
    bot.approve_chat_join_request(update.effective_chat.id, user_id)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Handle members requesting to join a chat
    dispatcher.add_handler(ChatJoinRequestHandler(welcome_new_members))

    # Start the Bot
    updater.start_polling(allowed_updates=[Update.CHAT_JOIN_REQUEST])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
