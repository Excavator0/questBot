from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import random
from database.db import Database
from keyboards.common_keyboards import build_hello_keyboard
from messages import *
from keyboards.run_keyboards import *

router = Router()


class RunnerStep(StatesGroup):
    main_menu = State()
    num = State()
    current = State()
    next = State()
    texts = State()
    ans = State()
    hints = State()
    final = State()
    contents = State()
    final_content = State()
    correct_msg = State()
    wrong_msg = State()
    desc = State()


async def main_menu(message: Message):
    await message.answer(
        text=hello_message,
        reply_markup=build_hello_keyboard().as_markup()
    )


@router.callback_query(F.data == "start_quest")
async def get_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=get_id_text
    )
    await state.set_state(RunnerStep.num)


@router.message(CommandStart(deep_link=True))
async def start_with_id(message: Message, command: CommandObject, state: FSMContext):
    quest_id = command.args
    db = Database("database/quests.db")
    db.cursor.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,))
    row = db.cursor.fetchone()
    if row is not None:
        if row[3] == 1:
            await message.answer("Автор закрыл доступ к этому квесту.")
        else:
            correct_msg = row[8].split(";")
            wrong_msg = row[9].split(";")
            for i in range(len(correct_msg)):
                correct_msg[i] = correct_msg[i].strip()
            for i in range(len(wrong_msg)):
                wrong_msg[i] = wrong_msg[i].strip()
            await state.update_data({"desc": row[5], "final": row[6], "final_content": row[7],
                                     "correct_msg": correct_msg, "wrong_msg": wrong_msg})
            await message.answer(text=row[5])

            db.cursor.execute("SELECT * FROM steps WHERE quest_id = ? ORDER BY num", (quest_id,))
            rows = db.cursor.fetchall()
            texts = []
            contents = []
            answers = []
            hints = []
            for row in rows:
                texts.append(row[3])
                answers.append(row[4])
                contents.append(row[5])
                hints.append(row[6])
            await state.update_data({"texts": texts, "ans": answers, "contents": contents,
                                     "hints": hints, "current": 1})
            await load_step(message, state)
    else:
        await message.answer("Квест был удален")
    db.conn.commit()
    db.close()


@router.message(RunnerStep.num)
async def load_quest_from_db(message: Message, state: FSMContext):
    quest_id = message.text
    if len(quest_id) == 8:
        db = Database("database/quests.db")
        db.cursor.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,))
        row = db.cursor.fetchone()
        if row is not None:
            if row[3] == 1:
                await message.answer("Автор закрыл доступ к этому квесту.")
            else:
                correct_msg = row[8].split(";")
                wrong_msg = row[9].split(";")
                for i in range(len(correct_msg)):
                    correct_msg[i] = correct_msg[i].strip()
                for i in range(len(wrong_msg)):
                    wrong_msg[i] = wrong_msg[i].strip()
                await state.update_data({"desc": row[5], "final": row[6], "final_content": row[7],
                                         "correct_msg": correct_msg, "wrong_msg": wrong_msg})
                await message.answer(text=row[5])

                db.cursor.execute("SELECT * FROM steps WHERE quest_id = ? ORDER BY num", (quest_id,))
                rows = db.cursor.fetchall()
                texts = []
                contents = []
                answers = []
                hints = []
                for row in rows:
                    texts.append(row[3])
                    answers.append(row[4])
                    contents.append(row[5])
                    hints.append(row[6])
                await state.update_data({"texts": texts, "ans": answers, "contents": contents,
                                         "hints": hints, "current": 1})
                await load_step(message, state)
        else:
            await message.answer("Введен неверный ID или такого квеста не существует.")
        db.conn.commit()
        db.close()
    else:
        await message.answer("Введен неверный ID или такого квеста не существует.")


async def load_step(message: Message, state: FSMContext):
    data = await state.get_data()
    cur = data["current"]
    texts = data["texts"]
    contents = data["contents"]
    if contents[cur - 1] is None:
        await message.answer(
            text=texts[cur - 1],
            reply_markup=run_keyboard().as_markup()
        )
    else:
        content_type = contents[cur - 1][contents[cur - 1].find(":") + 1:]
        if content_type == "video":
            await message.answer_video(
                video=contents[cur - 1][:contents[cur - 1].find(":")],
                caption=texts[cur - 1],
                reply_markup=run_keyboard().as_markup()
            )
        elif content_type == "photo":
            await message.answer_photo(
                photo=contents[cur - 1][:contents[cur - 1].find(":")],
                caption=texts[cur - 1],
                reply_markup=run_keyboard().as_markup()
            )
        else:
            await message.answer_document(
                document=contents[cur - 1][:contents[cur - 1].find(":")],
                caption=texts[cur - 1],
                reply_markup=run_keyboard().as_markup()
            )
    await state.set_state(RunnerStep.ans)


@router.message(RunnerStep.ans)
async def check_ans(message: Message, state: FSMContext):
    data = await state.get_data()
    cur = data["current"]
    answers = data["ans"]
    hints = data["hints"]
    correct_msg = data["correct_msg"]
    wrong_msg = data["wrong_msg"]
    user_ans = message.text
    if user_ans == "Выход":
        await state.clear()
        await main_menu(message)
    elif user_ans == "Подсказка":
        if hints[cur - 1] is None:
            await message.answer(text=no_hint)
        else:
            await message.answer(text=hints[cur - 1])
    else:
        if user_ans is None:
            await message.answer(text="Введите ответ текстом!")
        if user_ans.lower() == answers[cur - 1].lower():
            correct = random.choice(correct_msg)
            await message.answer(text=correct)
            if cur == len(answers):
                await load_final(message, state)
            else:
                await state.update_data({"current": cur + 1})
                await load_step(message, state)
        else:
            wrong = random.choice(wrong_msg)
            await message.answer(text=wrong)


async def load_final(message: Message, state: FSMContext):
    data = await state.get_data()
    final = data["final"]
    final_content = data["final_content"]
    if final_content is None:
        await message.answer(
            text=final,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        content_type = final_content[final_content.find(":") + 1:]
        if content_type == "video":
            await message.answer_video(
                video=final_content[:final_content.find(":")],
                caption=final,
                reply_markup=ReplyKeyboardRemove()
            )
        elif content_type == "photo":
            await message.answer_photo(
                photo=final_content[:final_content.find(":")],
                caption=final,
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer_document(
                document=final_content[:final_content.find(":")],
                caption=final,
                reply_markup=ReplyKeyboardRemove()
            )
    await state.clear()
