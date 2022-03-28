from pathlib import Path
from aiogram.types import CallbackQuery, Message, ContentTypes
from aiogram.dispatcher.storage import FSMContext

from common.schemas import CourierSchema
from telegram.loader import dp
from telegram.filters.users import IsCourier

from .states import InitStates
from .keyboards import proceed_final_keyboard
from .interfaces import DailyReportInternal, DAILY_REPORT
from .producers import upload_files


@DailyReportInternal.register()
@DAILY_REPORT()
async def daily_report(call: CallbackQuery, internal: DailyReportInternal):
    internal_new = DailyReportInternal(user_id=call.from_user.id)

    if internal and internal.closed and internal.dt.date() == internal_new.dt.date():
        await call.message.edit_text("Отчет за этот день уже был сдан")
        return

    await InitStates.mileage.set()
    await call.message.edit_text("Введи пробег по одометру")
    return {"internal": internal_new}


@DailyReportInternal.register()
@dp.message_handler(state=InitStates.mileage)
async def mileage_handler(message: Message, internal: DailyReportInternal):
    mileage_init = int(message.text)
    internal.data.update({"mileage_init": mileage_init})

    await InitStates.odometer.set()
    await message.answer("Пришли фото одометра")


@DailyReportInternal.register()
@dp.message_handler(
    IsCourier(),
    state=InitStates.odometer,
    is_media_group=False,
    content_types=ContentTypes.PHOTO,
)
async def odometer_handler(
    message: Message,
    state: FSMContext,
    internal: DailyReportInternal,
    courier: CourierSchema,
):
    photo = message.photo[-1]
    odometer = await photo.download(
        destination_file=f"{internal.path}/Одометр_{internal.dt.strftime('%Y_%m_%d')}"
    )
    internal.data.update({"odometer": Path(odometer.name)})

    files_data = await upload_files(internal.data, courier)
    internal.data.update(files_data)

    await message.answer(
        "Удачи! Не забудь закрыть отчет", reply_markup=proceed_final_keyboard
    )

    await state.reset_state(with_data=False)
