from typing import Optional, Union, Tuple, List, Dict

from telegram import Update
from telegram.ext import CommandHandler


class PrivateConversationCommandHandler(CommandHandler):
    def check_update(
        self, update: object
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, Dict]]]]]:
        if isinstance(update, Update) and update.effective_chat:
            if update.effective_chat.type != update.effective_chat.PRIVATE:
                return False

        return super().check_update(update)
