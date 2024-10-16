import logging
from aiogram import Bot, Dispatcher, types
import g4f
from aiogram.utils import executor

# Включите логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = '7448755655:AAHqKs0arVbnf45ocqyT-20L21O5Rhqonf4'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ID администратора (твой Telegram ID)
ADMIN_ID = 5623396563  # Замени это на свой Telegram ID

# Словарь для хранения истории разговоров
    conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history

@dp.message_handler(commands=['clear'])
async def process_clear_command(message: types.Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История диалога очищена.")

# Обработчик для каждого нового сообщения
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])
             
    chat_history = conversation_history[user_id]

    try:
        response = await g4f.ChatCompletion.create_async(
            model='gpt-4',
            messages=chat_history,
            provider=g4f.Provider.Bing,
        )
        chat_gpt_response = response
    except Exception as e:
        print(f"{g4f.Provider.Pizzagpt.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка."

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    print(conversation_history)
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    print(length)

    # Отправка ответа пользователю
    await message.answer(chat_gpt_response)

    # Отправка сообщения админу с запросом пользователя
    admin_message = f"Пользователь @{message.from_user.username} (ID: {user_id}) отправил сообщение:\n\n{user_input}"
    await bot.send_message(chat_id=ADMIN_ID,text=admin_message)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)