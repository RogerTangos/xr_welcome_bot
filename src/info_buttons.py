from abc import ABC
from pathlib import Path
from typing import Callable

from telegram.ext import CallbackContext

from src.i18n import get_user_language


# Abstract base class for a button that provides the user with a piece of information on click
class InfoButton(ABC):
    def __init__(self, button_text_provider: Callable[[CallbackContext], str]):
        self.__button_text_provider = button_text_provider

    def get_button_text(self, context: CallbackContext) -> str:
        return self.__button_text_provider(context)


# Button that sends the user a file when clicked
class FileInfoButton(InfoButton):
    def __init__(
        self,
        button_text_provider: Callable[[CallbackContext], str],
        local_filename: str,
        user_filename_provider: Callable[[CallbackContext], str],
    ):
        super().__init__(button_text_provider)
        self.__local_filename = local_filename
        self.__user_filename_provider = user_filename_provider

    def get_file_path(self, context: CallbackContext) -> Path:
        return (
            Path(__file__).parents[1]
            / "resources"
            / "files"
            / get_user_language(context)
            / self.__local_filename
        )

    def get_user_filename(self, context: CallbackContext) -> str:
        return self.__user_filename_provider(context)


# Button that sends the user a message when clicked
class TextInfoButton(InfoButton):
    def __init__(
        self,
        button_text_provider: Callable[[CallbackContext], str],
        info_text_provider: Callable[[CallbackContext], str],
    ):
        super().__init__(button_text_provider)
        self.__info_text_provider = info_text_provider

    def get_info_text(self, context: CallbackContext) -> str:
        return self.__info_text_provider(context)
