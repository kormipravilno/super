from pathlib import Path
import shutil
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.storage import FSMContext

from telegram.loader import dp, config
from telegram.keyboards.general import yes_no

from .interfaces import HasStateStartInternal
from .states import HasStateStartStates
from .keyboards import handlers_keyboard


@dp.message_handler(CommandStart())
async def start_cmd(message: Message):
    keyboard = await handlers_keyboard(message.from_user.id)
    await message.answer("Привет! Выбери действие...", reply_markup=keyboard)


@HasStateStartInternal.register()
@dp.message_handler(CommandStart(), state="*")
async def has_state_start_cmd(
    message: Message, internal: HasStateStartInternal, state: FSMContext
):
    internal = HasStateStartInternal(current_state=await state.get_state())
    text = (
        "❗ В данный момент выполняется другое действие. ❗\n"
        "<b>Прогресс по выполняемому действию сбросится.</b> Вернуться в главное меню?"
    )
    await HasStateStartStates.confirm.set()
    await message.answer(text, reply_markup=yes_no)

    return {"internal": internal}


@HasStateStartInternal.register()
@dp.message_handler(state=HasStateStartStates.confirm, text="Да")
async def proceed_has_state_start_cmd(message: Message, state: FSMContext):
    await message.answer("Прогресс обнулен", reply_markup=ReplyKeyboardRemove())

    await state.reset_state(with_data=False)
    shutil.rmtree(Path(config.TMP_FOLDER, str(message.from_user.id)))

    await start_cmd(message)

    return {"internal": None}


@HasStateStartInternal.register()
@dp.message_handler(state=HasStateStartStates.confirm, text="Нет")
async def cancel_has_state_start_cmd(
    message: Message, internal: HasStateStartInternal, state: FSMContext
):
    await message.answer(
        "Хорошо, остаемся на том же месте", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(internal.current_state)

    return {"internal": None}
