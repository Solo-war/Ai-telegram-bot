from aiogram.types import Message

from ai_telegram_bot.exceptions import CantGetFieldException


class UserInfo:
    def __init__(self, message: Message):
        id = message.from_user
        if id is None:
            raise CantGetFieldException(field_name=f"{message.from_user=}")
        text = message.text
        if text is None:
            raise CantGetFieldException(field_name=f"{message.text=}")

        self.id = id
        self.text = text
