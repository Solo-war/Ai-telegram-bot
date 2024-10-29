from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter

from ai_telegram_bot import states
from ai_telegram_bot.filters import ChatTypeFilter, TextFilter

from . import clear, start, taro, text, voice


def prepare_router() -> Router:
    user_router = Router(name="user_router")
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())
    user_router.message.register(
        start.start,
        TextFilter("🏠В главное меню"),
        StateFilter(states.user.UserMainMenu.menu),
    )

    user_router.message.register(taro.play, Command("taro"))
    user_router.message.register(clear.process_clear_command, Command("clear"))
    user_router.message.register(text.handle_message, F.text)
    user_router.message.register(voice.handle_voice_message, F.voice)

    return user_router
