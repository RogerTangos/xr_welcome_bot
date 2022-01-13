from typing import Optional, Union

from telegram import Update
from telegram.ext import CallbackQueryHandler


class PrivateConversationCallbackQueryHandler(CallbackQueryHandler):
    def check_update(self, update: object) -> Optional[Union[bool, object]]:
        if isinstance(update, Update) and update.effective_chat:
            if update.effective_chat.type != update.effective_chat.PRIVATE:
                return False

        return super().check_update(update)
