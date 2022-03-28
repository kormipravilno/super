from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.storage import FSMContext

from telegram.loader import dp

from .interfaces import CLEAR_STATE, ClearStateInternal
from .states import ClearStateStates


# TODO
@CLEAR_STATE(state=ClearStateStates.all_states)
async def recursive_clear_state(call: CallbackQuery):
    await call.message.edit_text("уже в процессе обнуления WIP")


@ClearStateInternal.register()
@CLEAR_STATE(state="*")
async def clear_state(call: CallbackQuery, state: FSMContext):
    s = await state.get_state()
    print(s)
    internal = ClearStateInternal(current_state=s)
    await ClearStateStates.user_id.set()

    await call.message.edit_text(
        "Введи ID пользователя, которому нужно обнулить состояние"
    )
    return {"internal": internal}


# TODO: clear state for specific dashboard handler
@ClearStateInternal.register()
@dp.message_handler(state=ClearStateStates.user_id)
async def clear_state_user_id(
    message: Message, internal: ClearStateInternal, state: FSMContext
):
    user_id = int(message.text)
    await dp.storage.reset_state(user=message.from_user.id)

    if user_id != message.from_user.id:
        await state.set_state(internal.current_state)

    await message.answer("Состояние пользователя успешно обнулено!")
    return {"internal": None}
