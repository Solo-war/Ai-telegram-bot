from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from tempfile import NamedTemporaryFile
from typing import Any

import ffmpeg
import speech_recognition as sr
from aiogram.types import Message

from ai_telegram_bot.exceptions import CantGetFieldException, RecognizeException


def get_file_id(message: Message):
    voice = message.voice
    if voice is None:
        raise CantGetFieldException(field_name=f"{message.voice=}")
    return voice.file_id


def get_bot(message: Message):
    bot = message.bot
    if bot is None:
        raise CantGetFieldException(field_name=f"{message.bot=}")
    return bot


@contextmanager
def convert_audio_format(
    input_path: str, output_format: str = ".wav"
) -> Generator[str, Any]:
    with NamedTemporaryFile(suffix=output_format) as tmp_file:
        output_path = tmp_file.name
        ffmpeg.input(input_path).output(output_path).run(overwrite_output=True)
        yield output_path


def recognize_audio(file_path: str) -> dict:
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="ru-RU")
        return {"text": text, "error": None}
    except sr.UnknownValueError:
        return {"text": None, "error": "Не удалось распознать голос."}
    except sr.RequestError:
        return {"text": None, "error": "Ошибка сервиса распознавания."}
    except Exception as e:
        return {"text": None, "error": str(e)}


@asynccontextmanager
async def download_voice(message: Message) -> AsyncGenerator[str, Any]:
    file_id = get_file_id(message)
    bot = get_bot(message)
    file = await bot.get_file(file_id)
    if file.file_path is None:
        raise CantGetFieldException(field_name=f"{file.file_path=}")
    with NamedTemporaryFile(suffix=".ogg") as tmp_file:
        temp_path = tmp_file.name
        await bot.download_file(file.file_path, temp_path)
        yield temp_path


async def convert_voice_to_text(message: Message) -> str:
    async with download_voice(message) as voice:
        with convert_audio_format(voice) as converted_file:
            result = recognize_audio(converted_file)

            if err_text := result.get("error"):
                raise RecognizeException(result=err_text)
            return result["text"]
