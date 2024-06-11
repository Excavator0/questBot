from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def build_hello_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Создать новый квест",
        callback_data="new_quest"
    ))
    builder.add(InlineKeyboardButton(
        text="Мои квесты",
        callback_data="my_quests"
    ))
    builder.add(InlineKeyboardButton(
        text="Скопировать квест по ID",
        callback_data="copy_quest"
    ))
    builder.add(InlineKeyboardButton(
        text="Пройти квест",
        callback_data="start_quest"
    ))
    builder.adjust(2, 2)
    return builder
