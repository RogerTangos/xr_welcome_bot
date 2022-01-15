from typing import Optional, Union, Dict, Tuple, List

from telegram import Update
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler


class PrivateConversationCallbackQueryHandler(CallbackQueryHandler):
    def check_update(self, update: object) -> Optional[Union[bool, object]]:
        if isinstance(update, Update) and update.effective_chat:
            if update.effective_chat.type != update.effective_chat.PRIVATE:
                return False

        return super().check_update(update)


class PrivateConversationCommandHandler(CommandHandler):
    def check_update(
        self, update: object
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, Dict]]]]]:
        if isinstance(update, Update) and update.effective_chat:
            if update.effective_chat.type != update.effective_chat.PRIVATE:
                return False

        return super().check_update(update)


class PrivateConversationMessageHandler(MessageHandler):
    def check_update(self, update: object) -> Optional[Union[bool, Dict[str, list]]]:
        if isinstance(update, Update) and update.effective_chat:
            if update.effective_chat.type != update.effective_chat.PRIVATE:
                return False

        return super().check_update(update)
