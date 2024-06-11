from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton


def run_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="Выход"
    ))
    builder.add(KeyboardButton(
        text="Подсказка"
    ))
    return builder
