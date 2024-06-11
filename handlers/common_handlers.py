from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from messages import *
from keyboards.common_keyboards import *

router = Router()


class Quest(StatesGroup):
    id = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        text=hello_message,
        reply_markup=build_hello_keyboard().as_markup()
    )

