from collections import defaultdict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from ai_telegram_bot.config import Settings
from ai_telegram_bot.general import convert_voice_to_text
from ai_telegram_bot.gpt import Gpt, GptArgs
from ai_telegram_bot.models import UserInfo

main_route = Router()
settings = Settings()
gpts = defaultdict(
    lambda: Gpt(
        GptArgs(
            model=settings.model,
            provider=settings.provider,
            proxy=settings.proxy,
            api_key=settings.api_key,
        )
    )
)


@main_route.message(Command("clear"))
async def process_clear_command(message: Message):
    user_id = UserInfo(message).id
    gpts.pop(user_id)
    await message.answer("История диалога очищена.")


async def answer_on_text(text: str, message: Message) -> None:
    user_id = UserInfo(message).id
    gpt = gpts[user_id]

    try:
        response = await gpt.ask(text)
    except Exception:
        response = "Извините, произошла ошибка."
    await message.answer(response)


@main_route.message(F.text)
async def handle_message(message: Message):
    text = UserInfo(message).text
    await answer_on_text(text, message)


@main_route.message(F.voice)
async def handle_voice_message(message: Message):
    text = await convert_voice_to_text(message)
    await answer_on_text(text, message)
