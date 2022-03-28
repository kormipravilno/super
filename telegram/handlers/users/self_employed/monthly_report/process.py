from pathlib import Path
from aiogram.types import CallbackQuery, Message, ContentTypes

from common.schemas import SelfEmployedGet, ContentType
from common.crud import se_service
from telegram.loader import dp
from telegram.filters.users import IsSelfEmployed

from .common import answer
from .interfaces import MRClosedInternal, MRInternal, Service, MONTHLY_REPORT
from .keyboards import service_callback
from .states import ProcessStates


@MRClosedInternal.register()
@MONTHLY_REPORT(IsSelfEmployed())
async def monthly_report(
    call: CallbackQuery,
    internal: MRClosedInternal,
    self_employed: SelfEmployedGet,
):
    internal_new = MRInternal(user_id=call.from_user.id)
    if (
        internal
        and internal.closed
        and internal.dt.year == internal_new.dt.year
        and internal.dt.month == internal_new.dt.month
    ):
        await call.message.edit_text("Отчет за этот месяц уже был сдан")
        return

    await ProcessStates.selection.set()
    await answer(call.message, internal_new, self_employed)
    return {"internal": internal_new}


@MRInternal.register()
@dp.callback_query_handler(
    IsSelfEmployed(),
    service_callback.filter(),
    state=ProcessStates.selection,
)
async def service_callback_handler(
    call: CallbackQuery,
    callback_data: dict,
    internal: MRInternal,
    self_employed: SelfEmployedGet,
):
    internal.current_service = await se_service.get(int(callback_data.get("id")))
    internal.set_current_message(call.message)

    if not (service := internal.get_service(internal.current_service.id)):
        if internal.current_service.type == ContentType.INT:
            await call.message.edit_text("Введи количество")
            await ProcessStates.value.set()
        elif internal.current_service.type == ContentType.PHOTOS:
            await call.message.edit_text("Пришли изображения")
            await ProcessStates.photo.set()
        elif internal.current_service.type == ContentType.BOOL:
            service = Service.from_value(internal.current_service, value=True)
            internal.services.append(service)
            internal.current_service = None
            await ProcessStates.selection.set()
            await answer(call.message, internal, self_employed)
    else:
        internal.delete_service(service)
        internal.set_current_message(None)
        await answer(call.message, internal, self_employed)


@MRInternal.register()
@dp.message_handler(IsSelfEmployed(), state=ProcessStates.value)
async def value_handler(
    message: Message,
    internal: MRInternal,
    self_employed: SelfEmployedGet,
):
    value = int(message.text)
    service = Service.from_value(internal.current_service, value=value)
    internal.services.append(service)

    internal.current_service = None
    await ProcessStates.selection.set()
    await answer(message, internal, self_employed)


@MRInternal.register()
@dp.message_handler(
    IsSelfEmployed(),
    is_media_group=True,
    content_types=ContentTypes.PHOTO,
    state=ProcessStates.photo,
)
async def photo_group_handler(
    message: Message,
    album: list[Message],
    internal: MRInternal,
    self_employed: SelfEmployedGet,
):
    msg = await message.answer("🤔 Загружаю данные...")
    await internal.current_message.delete()

    path = Path(internal.path, internal.current_service.name)
    for item in album:
        if photo_sizes := item.photo:
            photo = photo_sizes[-1]
            await photo.download(destination_file=Path(path, photo.file_id))
            await item.delete()

    service = Service.from_value(internal.current_service, value=path)
    internal.services.append(service)

    internal.current_service = None
    internal.set_current_message(None)
    await ProcessStates.selection.set()
    await answer(msg, internal, self_employed)


@MRInternal.register()
@dp.message_handler(
    IsSelfEmployed(),
    is_media_group=False,
    content_types=ContentTypes.PHOTO,
    state=ProcessStates.photo,
)
async def photo_handler(
    message: Message,
    internal: MRInternal,
    self_employed: SelfEmployedGet,
):
    await photo_group_handler(message, [message], internal, self_employed)
