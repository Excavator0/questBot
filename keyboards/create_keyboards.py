from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def copy_or_new_step():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Создать шаг самому",
        callback_data="next_step"
    ))
    builder.add(InlineKeyboardButton(
        text="Скопировать шаг по ID квеста и номеру шага",
        callback_data="copy_step"
    ))
    builder.adjust(1, 1)
    return builder


def after_ans_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Добавить следующий шаг",
        callback_data="copy_or_new"
    ))
    builder.add(InlineKeyboardButton(
        text="Добавить/изменить финальный шаг",
        callback_data="set_final"
    ))
    builder.add(InlineKeyboardButton(
        text="Перейти к шагу по номеру",
        callback_data="get_step"
    ))
    builder.adjust(2, 1)
    return builder


def final_keyboard(locked):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Изменить название",
        callback_data="edit_name"
    ))
    builder.add(InlineKeyboardButton(
        text="Изменить описание",
        callback_data="edit_desc"
    ))
    builder.add(InlineKeyboardButton(
        text="Изменить контент финала",
        callback_data="set_final"
    ))
    builder.add(InlineKeyboardButton(
        text="Перейти к шагу по номеру",
        callback_data="get_step"
    ))
    builder.add(InlineKeyboardButton(
        text="Изменить реакции на ответ",
        callback_data="edit_response"
    ))
    if locked == 1:
        lock_text = "Открыть доступ по ID"
    else:
        lock_text = "Закрыть доступ по ID"
    builder.add(InlineKeyboardButton(
        text=lock_text,
        callback_data="lock_quest"
    ))
    builder.add(InlineKeyboardButton(
        text="Ссылка на квест",
        callback_data="get_link"
    ))
    builder.add(InlineKeyboardButton(
        text="Удалить квест",
        callback_data="delete_quest"
    ))
    builder.add(InlineKeyboardButton(
        text="Добавить еще один шаг",
        callback_data="copy_or_new"
    ))
    builder.add(InlineKeyboardButton(
        text="Сохранить квест",
        callback_data="quest_done"
    ))
    builder.adjust(2, 2, 2, 2, 1, 1)
    return builder


def edit_step():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Изменить текст шага",
        callback_data="edit_step_text"
    ))
    builder.add(InlineKeyboardButton(
        text="Изменить ответ шага",
        callback_data="edit_step_ans"
    ))
    builder.add(InlineKeyboardButton(
        text="Изменить подсказку",
        callback_data="edit_step_hint"
    ))
    builder.add(InlineKeyboardButton(
        text="Удалить шаг",
        callback_data="remove_step"
    ))
    builder.add(InlineKeyboardButton(
        text="Перейти к другому шагу",
        callback_data="get_step"
    ))
    builder.add(InlineKeyboardButton(
        text="Перейти к финальному шагу",
        callback_data="get_final"
    ))
    builder.add(InlineKeyboardButton(
        text="Добавить следующий шаг",
        callback_data="copy_or_new"
    ))
    builder.add(InlineKeyboardButton(
        text="Сохранить квест",
        callback_data="quest_done"
    ))
    builder.adjust(2, 2, 2, 1, 1)
    return builder


def after_rm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Добавить/изменить финальный шаг",
        callback_data="get_final"
    ))
    builder.add(InlineKeyboardButton(
        text="Перейти к шагу по номеру",
        callback_data="get_step"
    ))
    builder.adjust(1, 1)
    return builder


def no_final_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Добавить финал",
        callback_data="set_final"
    ))
    builder.add(InlineKeyboardButton(
        text="Перейти к шагу по номеру",
        callback_data="get_step"
    ))
    builder.add(InlineKeyboardButton(
        text="Добавить следующий шаг",
        callback_data="copy_or_new"
    ))
    builder.adjust(2, 1)
    return builder


def my_quests_keyboard(data):
    builder = InlineKeyboardBuilder()
    for quest_id, name in data:
        builder.add(InlineKeyboardButton(
            text=(quest_id + " - " + name),
            callback_data=("edit_quest_" + quest_id)
        ))
    builder.adjust(1)
    return builder