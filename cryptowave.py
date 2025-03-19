import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties

# Укажите ваш токен бота
TOKEN = "8101923955:AAEkYdACeI3H78tRhQeEtDVSjiEnhIUyrgs"

# Укажите ID владельца бота (ваш Telegram ID)
OWNER_ID = 7496432981  # 🔹 Укажите ваш Telegram ID

# Укажите реквизиты для оплаты и ссылку на отзывы
PAYMENT_DETAILS = "Реквизиты для оплаты:\n\n🔹 Кошелек: 2200 7010 7876 6976\n🔹 Банк: Т-Банк\n🔹 Комментарий: 'Оплата'"
REVIEWS_LINK = "Отзывы: https://t.me/+GB1kEBqwcoJmNjBi"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))  # ✅ Исправлено
dp = Dispatcher()

# Храним пользователей, отправивших запрос в техподдержку
support_requests = {}

# Создание клавиатуры с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Реквизиты"), KeyboardButton(text="Отзывы")],
        [KeyboardButton(text="Сроки")],
        [KeyboardButton(text="Подтверждение оплаты")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: types.Message):
    """Приветственное сообщение с клавиатурой"""
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)


@dp.message(F.text == "Реквизиты")
async def send_payment_info(message: types.Message):
    """Отправка реквизитов для оплаты"""
    await message.answer(PAYMENT_DETAILS)


@dp.message(F.text == "Отзывы")
async def send_reviews_link(message: types.Message):
    """Отправка ссылки на отзывы"""
    await message.answer(f"Ознакомьтесь с отзывами тут:\n{REVIEWS_LINK}")


@dp.message(F.text == "Сроки")
async def track_investment(message: types.Message):
    """Начало отслеживания вклада (48 часов)"""
    await message.answer("✅ Если вы сделали вклад, ожидайте 48 часов.")


@dp.message(F.text == "Подтверждение оплаты")
async def support_start(message: types.Message):
    """Начало общения с техподдержкой"""
    user_id = message.from_user.id
    support_requests[user_id] = True
    await message.answer("📝 📝 Пожалуйста, отправьте квитанцию (чек) и номер карты вместе с фото. Если какой-то из пунктов нарушен - есть шанс, что деньги прийдут не вам.")


@dp.message(F.text | F.photo)
async def forward_to_owner(message: types.Message):
    """Пересылает сообщение и фото в поддержку владельцу"""
    user_id = message.from_user.id

    if user_id in support_requests:
        del support_requests[user_id]

        caption = f"📩 Новое сообщение от {hbold(message.from_user.full_name)} ({user_id}):\n\n"
        caption += message.caption if message.caption else message.text if message.text else "Без текста"

        if message.photo:
            photo = message.photo[-1].file_id
            await bot.send_photo(OWNER_ID, photo=photo, caption=caption)
        else:
            await bot.send_message(OWNER_ID, caption)

        await message.answer("✅ Ваше подтверждение отправлено. Ожидайте выплаты.")


@dp.message(Command("reply"))
async def reply_to_user(message: types.Message):
    """Владелец бота отвечает пользователю"""
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("⚠ Используйте формат: /reply user_id ваш ответ")
        return

    user_id = int(args[1])
    reply_text = args[2]

    try:
        await bot.send_message(user_id, f"📩 Ответ от техподдержки:\n\n{reply_text}")
        await message.answer("✅ Ответ отправлен пользователю.")
    except Exception:
        await message.answer("❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.")


async def main():
    """Функция запуска бота"""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())