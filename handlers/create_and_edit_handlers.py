import uuid
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link
from database.db import Database
from messages import *
from keyboards.create_keyboards import *

router = Router()


class Step(StatesGroup):
    id = State()
    current = State()
    copy_step = State()
    num = State()
    name = State()
    desc = State()
    texts = State()
    ans = State()
    step = State()
    final = State()
    correct_msg = State()
    wrong_msg = State()
    contents = State()
    final_content = State()
    hints = State()
    locked = State()
    edit_name = State()
    edit_desc = State()
    edit_step = State()
    edit_ans = State()
    edit_hint = State()
    edit_final = State()


@router.callback_query(F.data == "new_quest")
async def create_new(callback: CallbackQuery, state: FSMContext):
    quest_id = str(uuid.uuid4())[:8]
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=new_quest(quest_id)
    )
    await state.set_data({"num": 0, "current": 0, "texts": [], "ans": [], "final": "", "id": quest_id,
                          "correct_msg": "Правильно!",
                          "wrong_msg": "Ответ неверный!", "contents": [], "locked": 0, "hints": []})
    await state.set_state(Step.name)


@router.message(Step.name)
async def set_quest_name(message: Message, state: FSMContext):
    name = message.text
    if name is None:
        await message.answer(
            text="Введите название текстом!"
        )
    else:
        await state.update_data({"name": name})
        await message.answer(text=set_desc)
        await state.set_state(Step.desc)


@router.message(Step.desc)
async def set_quest_desc(message: Message, state: FSMContext):
    desc = message.text
    if desc is None:
        await message.answer(
            text="Введите описание текстом!"
        )
    else:
        await state.update_data({"desc": desc})
        await message.answer(
            text=new_or_copy_text,
            reply_markup=copy_or_new_step().as_markup()
        )


@router.callback_query(F.data == "copy_or_new")
async def copy_or_new(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=new_or_copy_text,
        reply_markup=copy_or_new_step().as_markup()
    )


@router.callback_query(F.data == "copy_step")
async def copy_step_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text="Введите ID квеста и номер шага через пробел"
    )
    await state.set_state(Step.copy_step)


@router.message(Step.copy_step)
async def copy_step(message: Message, state: FSMContext):
    query = message.text
    space_pos = query.find(" ")
    if space_pos == -1:
        await message.answer(text="ID квеста и номер шага введены неверно. Введите ID квеста и номер шага через пробел")
    else:
        quest_id = query[:space_pos]
        step_num = query[space_pos + 1:]
        data = await state.get_data()
        texts = data["texts"]
        answers = data["ans"]
        contents = data["contents"]
        hints = data["hints"]
        current = data["current"]
        db = Database("database/quests.db")
        db.cursor.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,))
        row = db.cursor.fetchone()
        if row is not None:
            if row[3] == 1:
                await message.answer(text="Автор закрыл доступ к этому квесту.")
            else:
                db.cursor.execute("SELECT * FROM steps WHERE quest_id = ? AND num = ?", (quest_id, step_num,))
                row = db.cursor.fetchone()
                if row is None:
                    await message.answer(text="Неверный номер шага")
                else:
                    texts.append(row[3])
                    answers.append(row[4])
                    contents.append(row[5])
                    hints.append(row[6])
                    current = current + 1
                    await state.update_data({"texts": texts, "ans": answers, "contents": contents,
                                             "hints": hints, "current": current, "num": current-1})
                    await message.answer(
                        text="Шаг успешно скопирован. Выберите следующее действие",
                        reply_markup=after_ans_keyboard().as_markup()
                    )
        else:
            await message.answer(text="ID квеста введен неверно")
        db.conn.commit()
        db.close()


@router.message(Step.num)
async def add_next_step(message: Message, state: FSMContext):
    data = await state.get_data()
    texts = data["texts"]
    contents = data["contents"]
    num = data["num"]
    content_id = None
    if message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]:
        if message.content_type == ContentType.TEXT:
            step_text = message.text
        else:
            if message.content_type == ContentType.PHOTO:
                content_id = message.photo[0].file_id + ":photo"
            elif message.content_type == ContentType.VIDEO:
                content_id = message.video.file_id + ":video"
            else:
                content_id = message.document.file_id + ":doc"
            step_text = message.caption
        contents.append(content_id)
        if step_text is None:
            step_text = ""
        texts.append(step_text)
        await message.answer(
            text=add_ans
        )
        num = num + 1
        await state.update_data({"texts": texts, "num": num, "contents": contents})
        await state.set_state(Step.ans)
    else:
        await message.answer(text=wrong_file)


@router.message(Step.ans)
async def add_next_ans(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data["ans"]
    if message.content_type == ContentType.TEXT:
        ans_text = message.text
        answers.append(ans_text)
        await state.update_data({"ans": answers})
        await state.set_state(Step.hints)
        await message.answer(
            text=ans_added
        )
    else:
        await message.answer(
            text="Введите ответ текстом!"
        )


@router.message(Step.hints)
async def add_hint(message: Message, state: FSMContext):
    if message.text == "-":
        hint = None
    else:
        hint = message.text
    data = await state.get_data()
    hints = data["hints"]
    hints.append(hint)
    await state.update_data({"hints": hints})
    await message.answer(
        text=hint_added,
        reply_markup=after_ans_keyboard().as_markup()
    )


@router.callback_query(F.data == "next_step")
async def set_next_step(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data["current"]
    await callback.message.delete_reply_markup()
    current = current + 1
    await callback.message.edit_text(
        text=f"Введите текст шага {current}. Можете приложить фото, видео или файл"
    )
    await state.update_data({"current": current})
    await state.set_state(Step.num)


@router.callback_query(F.data == "get_final")
async def get_final(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        final = data["final"]
        final_content = data["final_content"]
        locked = data["locked"]
        await callback.message.delete_reply_markup()
        await callback.message.answer(text="Текущий финал: ")
        if final_content is None:
            await callback.message.answer(
                text=final
            )
        else:
            content_type = final_content[final_content.find(":") + 1:]
            if content_type == "video":
                await callback.message.answer_video(
                    video=final_content[:final_content.find(":")],
                    caption=final
                )
            elif content_type == "photo":
                await callback.message.answer_photo(
                    photo=final_content[:final_content.find(":")],
                    caption=final
                )
            else:
                await callback.message.answer_document(
                    document=final_content[:final_content.find(":")],
                    caption=final
                )
        await callback.message.answer(
            text="Выберите следующее действие",
            reply_markup=final_keyboard(locked).as_markup()
        )
    except KeyError:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text="Финал пока не установлен",
            reply_markup=no_final_keyboard().as_markup()
        )


@router.callback_query(F.data == "set_final")
async def set_final(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text="Введите текст финального шага. Можете приложить фото, видео или файл")
    await state.set_state(Step.edit_final)


@router.message(Step.final)
async def check_final(message: Message, state: FSMContext):
    content_id = None
    data = await state.get_data()
    locked = data["locked"]
    if message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]:
        if message.content_type == ContentType.TEXT:
            final_text = message.text
        else:
            if message.content_type == ContentType.PHOTO:
                content_id = message.photo[0].file_id + ":photo"
            elif message.content_type == ContentType.VIDEO:
                content_id = message.video.file_id + ":video"
            else:
                content_id = message.document.file_id + ":doc"
            final_text = message.caption
        if final_text is None:
            final_text = ""
        await message.answer(
            text=out_final(final_text),
            reply_markup=final_keyboard(locked).as_markup()
        )
        await state.update_data({"final": final_text, "final_content": content_id})
    else:
        await message.answer(
            text=wrong_file
        )


@router.callback_query(F.data == "get_step")
async def get_step(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=get_step_text
    )
    await state.set_state(Step.step)


@router.message(Step.step)
async def get_step_by_num(message: Message, state: FSMContext):
    data = await state.get_data()
    num = data["num"]
    step_num = message.text
    try:
        step_num = int(step_num)
        isnum = True
    except ValueError:
        isnum = False
    if isnum:
        if 0 < step_num < int(num):
            texts = data["texts"]
            contents = data["contents"]
            answers = data["ans"]
            hints = data["hints"]
            current = data["current"]
            await message.answer(
                text=f"Текст шага {step_num}:\n{texts[step_num - 1]}"
            )
            if contents[step_num - 1] is not None:
                content_type = contents[step_num - 1][contents[step_num - 1].find(":") + 1:]
                if content_type == "video":
                    await message.answer_video(
                        video=contents[step_num - 1][:contents[step_num - 1].find(":")],
                    )
                elif content_type == "photo":
                    await message.answer_photo(
                        photo=contents[step_num - 1][:contents[step_num - 1].find(":")],
                    )
                else:
                    await message.answer_document(
                        document=contents[step_num - 1][:contents[step_num - 1].find(":")],
                    )
            await message.answer(
                text=f"Текст ответа:\n{answers[step_num - 1]}"
            )
            if hints[step_num - 1] is not None:
                await message.answer(
                    text=f"Текст подсказки:\n{hints[step_num - 1]}\n\nВыберите следующее действие",
                    reply_markup=edit_step().as_markup()
                )
            else:
                await message.answer(
                    text="Подсказки для этого шага нет \n\nВыберите следующее действие",
                    reply_markup=edit_step().as_markup()
                )
            current = current + 1
            await state.update_data({"current": current})
        else:
            await message.answer(
                text="Неверное значение шага\n" + get_step_text
            )
    else:
        await message.answer(
            text="Неверное значение шага\n" + get_step_text
        )


@router.callback_query(F.data == "quest_done")
async def save_to_db(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    try:
        final = data["final"]
        db = Database("database/quests.db")
        quest_id = data["id"]
        db.cursor.execute("DELETE FROM quests WHERE quest_id = ?", (quest_id,))
        db.cursor.execute("DELETE FROM steps WHERE quest_id = ?", (quest_id,))
        db.cursor.execute("INSERT INTO quests (author_id, quest_id, locked, name, desc, final, "
                          "final_content_id, correct_msg, wrong_msg) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (user_id, data["id"], data["locked"], data["name"], data["desc"], data["final"],
                           data["final_content"], data["correct_msg"], data["wrong_msg"]))
        texts = data["texts"]
        answers = data["ans"]
        contents = data["contents"]
        hints = data["hints"]
        for i in range(len(texts)):
            db.cursor.execute(
                "INSERT INTO steps (quest_id, num, text, answer, content_id, hint) "
                "VALUES (?, ?, ?, ?, ?, ?)", (data["id"], i + 1, texts[i], answers[i], contents[i], hints[i]))
        db.conn.commit()
        db.close()
        link = await create_start_link(callback.bot, quest_id)
        await callback.message.delete_reply_markup()
        await callback.message.answer(
            text=(quest_saved + "\nСсылка на квест: " + link)
        )
        await state.clear()
    except KeyError:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text="Нет финального шага!\nНеобходимо добавить финал",
            reply_markup=edit_step().as_markup()
        )


@router.callback_query(F.data == "edit_response")
async def edit_response(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    correct_msg = data["correct_msg"]
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=edit_correct_msg(correct_msg)
    )
    await state.set_state(Step.correct_msg)


@router.message(Step.correct_msg)
async def edit_correct_response(message: Message, state: FSMContext):
    data = await state.get_data()
    wrong_msg = data["wrong_msg"]
    correct_msg = message.text
    await message.answer(
        text=edit_wrong_msg(wrong_msg)
    )
    await state.update_data({"correct_msg": correct_msg})
    await state.set_state(Step.wrong_msg)


@router.message(Step.wrong_msg)
async def edit_wrong_response(message: Message, state: FSMContext):
    wrong_msg = message.text
    data = await state.get_data()
    locked = data["locked"]
    await message.answer(
        text=response_saved,
        reply_markup=final_keyboard(locked).as_markup()
    )
    await state.update_data({"wrong_msg": wrong_msg})


@router.callback_query(F.data == "remove_step")
async def delete_step(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    texts = data["texts"]
    answers = data["ans"]
    contents = data["contents"]
    hints = data["hints"]
    current = data["current"]
    num = data["num"]
    if len(texts) == 1:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text="В квесте должен быть хотя бы один шаг!",
            reply_markup=edit_step().as_markup()
        )
    else:
        texts.pop(current - 1)
        answers.pop(current - 1)
        contents.pop(current - 1)
        hints.pop(current - 1)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text=step_removed,
            reply_markup=after_rm_keyboard().as_markup()
        )
        await state.update_data({"texts": texts, "answers": answers, "contents": contents,
                                 "hints": hints, "current": current - 1, "num": num - 1})


@router.callback_query(F.data == "my_quests")
async def show_my_quests(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db = Database("database/quests.db")
    db.cursor.execute("SELECT * FROM quests WHERE author_id = ?", (user_id,))
    rows = db.cursor.fetchall()
    db.conn.commit()
    db.close()
    data = []
    for row in rows:
        data.append((row[2], row[4]))
    await state.clear()
    await callback.message.delete_reply_markup()
    if len(data) == 0:
        await callback.message.edit_text(text="Квесты не найдены")
    else:
        await callback.message.edit_text(
            text="Выберите квест, который хотите отредактировать",
            reply_markup=my_quests_keyboard(data).as_markup()
        )


@router.callback_query(F.data.startswith("edit_quest_"))
async def load_quest(callback: CallbackQuery, state: FSMContext):
    quest_id = callback.data[callback.data.rfind("_") + 1:]
    db = Database("database/quests.db")
    db.cursor.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,))
    row = db.cursor.fetchone()
    locked = row[3]
    await state.update_data({"locked": row[3], "name": row[4], "desc": row[5], "final": row[6], "final_content": row[7],
                             "correct_msg": row[8], "wrong_msg": row[9]})

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
                             "hints": hints, "current": len(rows) + 1, "num": len(rows), "id": quest_id})
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=edit_quest_text(quest_id),
        reply_markup=final_keyboard(locked).as_markup()
    )
    db.conn.commit()
    db.close()


@router.callback_query(F.data == "edit_step_text")
async def get_step_content(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data["current"]
    await callback.message.delete_reply_markup()
    await callback.message.answer(text=f"Введите текст шага {current}. Можете приложить фото, видео или файл")
    await state.set_state(Step.edit_step)


@router.message(Step.edit_step)
async def edit_step_content(message: Message, state: FSMContext):
    data = await state.get_data()
    cur = data["current"]
    texts = data["texts"]
    contents = data["contents"]
    content_id = None
    if message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]:
        if message.content_type == ContentType.TEXT:
            step_text = message.text
        else:
            if message.content_type == ContentType.PHOTO:
                content_id = message.photo[0].file_id + ":photo"
            elif message.content_type == ContentType.VIDEO:
                content_id = message.video.file_id + ":video"
            else:
                content_id = message.document.file_id + ":doc"
            step_text = message.caption
        contents[cur - 1] = content_id
        if step_text is None:
            step_text = ""
        texts[cur - 1] = step_text
        await state.update_data({"texts": texts, "contents": contents})
        await message.answer(
            text="Контент шага изменен. Выберите следующее действие",
            reply_markup=edit_step().as_markup()
        )
    else:
        await message.answer(text=wrong_file)


@router.callback_query(F.data == "edit_step_ans")
async def get_ans_content(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="Введите текст ответа")
    await state.set_state(Step.edit_ans)


@router.message(Step.edit_ans)
async def edit_step_content(message: Message, state: FSMContext):
    data = await state.get_data()
    cur = data["current"]
    answers = data["ans"]
    if message.content_type == ContentType.TEXT:
        answer = message.text
        answers[cur - 1] = answer
        await state.update_data({"ans": answers})
        await state.set_state(Step.hints)
        await message.answer(
            text="Ответ изменен. Выберите следующее действие",
            reply_markup=edit_step().as_markup()
        )
    else:
        await message.answer(
            text="Введите ответ текстом!"
        )


@router.callback_query(F.data == "edit_step_hint")
async def get_hint_content(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="Введите текст подсказки")
    await state.set_state(Step.edit_hint)


@router.message(Step.edit_hint)
async def edit_hint_content(message: Message, state: FSMContext):
    data = await state.get_data()
    cur = data["current"]
    hints = data["hints"]
    hint = message.text
    hints[cur - 1] = hint
    await state.update_data({"hints": hints})
    await message.answer(
        text="Подсказка изменена. Выберите следующее действие",
        reply_markup=edit_step().as_markup()
    )


@router.callback_query(F.data == "edit_name")
async def get_new_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    data = await state.get_data()
    name = data["name"]
    await callback.message.answer(text=f"Текущее название: {name}")
    await callback.message.answer(text="Введите новое название")
    await state.set_state(Step.edit_name)


@router.message(Step.edit_name)
async def edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    locked = data["locked"]
    new_name = message.text
    await state.update_data({"name": new_name})
    await message.answer(
        text="Название изменено. Выберите следующее действие",
        reply_markup=final_keyboard(locked).as_markup()
    )


@router.callback_query(F.data == "edit_desc")
async def get_new_desc(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    data = await state.get_data()
    desc = data["desc"]
    await callback.message.answer(text=f"Текущее описание: {desc}")
    await callback.message.answer(text="Введите новое описание")
    await state.set_state(Step.edit_desc)


@router.message(Step.edit_desc)
async def edit_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    locked = data["locked"]
    new_desc = message.text
    await state.update_data({"desc": new_desc})
    await message.answer(
        text="Описание изменено. Выберите следующее действие",
        reply_markup=final_keyboard(locked).as_markup()
    )


@router.message(Step.edit_final)
async def edit_final_content(message: Message, state: FSMContext):
    data = await state.get_data()
    locked = data["locked"]
    content_id = None
    if message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]:
        if message.content_type == ContentType.TEXT:
            final_text = message.text
        else:
            if message.content_type == ContentType.PHOTO:
                content_id = message.photo[0].file_id + ":photo"
            elif message.content_type == ContentType.VIDEO:
                content_id = message.video.file_id + ":video"
            else:
                content_id = message.document.file_id + ":doc"
            final_text = message.caption
        final_content = content_id
        final = final_text
        await state.update_data({"final": final, "final_content": final_content})
        await message.answer(
            text="Контент финала изменен. Выберите следующее действие",
            reply_markup=final_keyboard(locked).as_markup()
        )
    else:
        await message.answer(text=wrong_file)


@router.callback_query(F.data == "lock_quest")
async def lock_quest(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    locked = data["locked"]
    if locked == 1:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text="Доступ к квесту по ID открыт. Выберите следующее действие",
            reply_markup=final_keyboard(0).as_markup()
        )
        await state.update_data({"locked": 0})
    else:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text="Доступ к квесту по ID закрыт. Выберите следующее действие",
            reply_markup=final_keyboard(1).as_markup()
        )
        await state.update_data({"locked": 1})


@router.callback_query(F.data == "copy_quest")
async def get_id_to_copy(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text="Введите ID квеста, который хотите скопировать"
    )
    await state.set_state(Step.locked)


@router.message(Step.locked)
async def copy_by_id(message: Message, state: FSMContext):
    new_quest_id = str(uuid.uuid4())[:8]
    quest_id = message.text
    if len(quest_id) == 8:
        db = Database("database/quests.db")
        db.cursor.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,))
        row = db.cursor.fetchone()
        if row is not None:
            if row[3] == 1:
                await message.answer("Автор закрыл доступ к этому квесту.")
            else:
                locked = row[3]
                await state.update_data({"id": new_quest_id, "locked": row[3], "name": row[4], "desc": row[5],
                                         "final": row[6], "final_content": row[7],
                                         "correct_msg": row[8], "wrong_msg": row[9]})

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
                                         "hints": hints, "current": len(rows) + 1, "num": len(rows)})
                await message.answer(
                    text=copied_quest_text(quest_id, new_quest_id),
                    reply_markup=final_keyboard(locked).as_markup()
                )
        else:
            await message.answer("Введен неверный ID или такого квеста не существует.")
        db.conn.commit()
        db.close()
    else:
        await message.answer("Введен неверный ID или такого квеста не существует.")


@router.callback_query(F.data == "delete_quest")
async def delete_quest(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    data = await state.get_data()
    quest_id = data["id"]
    db = Database("database/quests.db")
    db.cursor.execute("DELETE FROM quests WHERE quest_id = ?", (quest_id,))
    db.cursor.execute("DELETE FROM steps WHERE quest_id = ?", (quest_id,))
    db.conn.commit()
    db.close()
    await callback.message.answer(text=f"Квест {quest_id} удален!")
    await state.clear()


@router.callback_query(F.data == "get_link")
async def get_link(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quest_id = data["id"]
    link = await create_start_link(callback.bot, quest_id)
    await callback.message.edit_text(text=link)
