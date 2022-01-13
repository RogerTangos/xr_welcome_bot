from typing import Optional, Union, Dict

from telegram import Update
from telegram.ext import MessageHandler


class PrivateConversationMessageHandler(MessageHandler):
    def check_update(self, update: object) -> Optional[Union[bool, Dict[str, list]]]:
        if isinstance(update, Update) and update.effective_chat:
            if update.effective_chat.type != update.effective_chat.PRIVATE:
                return False

        return super().check_update(update)
