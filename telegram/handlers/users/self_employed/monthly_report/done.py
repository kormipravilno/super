from datetime import datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta
from aiogram.types import (
    CallbackQuery,
    Message,
    ContentTypes,
    ReplyKeyboardRemove,
)
from aiogram.types.input_file import InputFile
from aiogram.dispatcher.storage import FSMContext

from common.schemas import SelfEmployedGet, ContentType
from common.crud import se_service
from telegram.loader import dp, config
from telegram.filters.users import IsSelfEmployed

from .common import answer, services_to_text
from .interfaces import (
    MRInternal,
    MonthlyReportExternal,
    MROfficialInternal,
    MRUploadedInternal,
    Info,
    Datetime,
)
from .keyboards import service_callback, is_okay
from .states import ProcessStates, FinalStates
from .producers import (
    upload_files,
    create_folder,
    upload_data,
    construct_doc,
    upload_file,
)


@MRInternal.register()
@dp.callback_query_handler(
    service_callback.filter(id="0"),
    state=ProcessStates.selection,
)
async def done_callback_handler(
    call: CallbackQuery,
    internal: MRInternal,
):
    info = Info.from_services(internal.services)
    text = (
        "Все правильно?\n"
        f"Общая стоимость услуг составляет <b>{info.payout.total}₽</b>\n\n"
        f"{services_to_text(internal.services, payout=True)}"
    )

    current_message = await call.message.answer(
        text,
        reply_markup=is_okay,
    )
    internal.set_current_message(current_message)
    await call.message.delete()
    await ProcessStates.is_okay.set()


@MRInternal.register()
@dp.message_handler(
    IsSelfEmployed(),
    state=ProcessStates.is_okay,
    text="✅ Да, все верно!",
)
async def okay_handler(
    message: Message,
    internal: MRInternal,
    state: FSMContext,
    self_employed: SelfEmployedGet,
):
    msg = await message.answer(
        "🤔 Загружаю данные...", reply_markup=ReplyKeyboardRemove()
    )

    folder = await create_folder(internal.dt, self_employed)
    services = await upload_files(internal.services, folder["id"])
    info = Info.from_services(internal.services)

    internal_uploaded = internal.to_uploaded(folder["id"])
    external = MonthlyReportExternal(
        self_employed=self_employed,
        services=services,
        url=folder["webViewLink"],
        info=info,
        dt_start=Datetime.from_datetime(internal.dt),
        dt_end=Datetime.from_datetime(),
    )

    record = await upload_data(external)
    if self_employed.template_id:
        path = await construct_doc(
            external,
            self_employed,
            folder["id"],
            internal.path,
        )
        await message.answer_document(
            InputFile(path),
            caption="Распечатай этот документ, подпиши и пришли фото",
        )
        await msg.delete()
        await FinalStates.doc.set()
        return {"internal": internal_uploaded}
    else:
        await message.answer("✅ Спасибо, отчет успешно загружен!")
        await msg.delete()
        await state.reset_state(with_data=False)
        internal.cleanup()
        return {"internal": internal.to_closed()}


@MRInternal.register()
@dp.message_handler(
    IsSelfEmployed(),
    state=ProcessStates.is_okay,
    text="↩️ Мне нужно что-то изменить...",
)
async def not_okay_handler(
    message: Message,
    internal: MRInternal,
    self_employed: SelfEmployedGet,
):
    await ProcessStates.selection.set()
    await answer(message, internal, self_employed)


@MRUploadedInternal.register()
@dp.message_handler(
    IsSelfEmployed(),
    content_types=ContentTypes.PHOTO,
    is_media_group=False,
    state=FinalStates.doc,
)
async def doc_handler(message: Message, internal: MRUploadedInternal):
    msg = await message.answer("🤔 Загружаю данные...")

    path = Path(internal.path, "Акт подписанный")
    await message.photo[-1].download(destination_file=path)
    await upload_file(path, internal.folder_id)

    receipt_until_dt = internal.dt + relativedelta(months=1, day=15)
    internal_official = internal.to_official(receipt_until_dt.date())
    await message.answer("✅ Спасибо, отчет успешно загружен!")
    await message.answer(
        f"Я буду ждать чек до {internal_official.receipt_until.strftime('%d.%m.%Y')}"
    )
    await msg.delete()

    await FinalStates.receipt.set()
    return {"internal": internal_official}


@MROfficialInternal.register()
@dp.message_handler(
    IsSelfEmployed(),
    content_types=ContentTypes.PHOTO,
    is_media_group=False,
    state=FinalStates.receipt,
)
async def receipt_handler(
    message: Message,
    state: FSMContext,
    internal: MROfficialInternal,
):
    date_now = datetime.now(config.TIMEZONE).date()
    if date_now > internal.receipt_until:
        await message.answer("Кажется, вы не успели сдать чек :(")
        return

    msg = await message.answer("🤔 Загружаю данные...")
    path = Path(internal.path, "Чек")
    await message.photo[-1].download(destination_file=path)
    await upload_file(path, internal.folder_id)

    await message.answer("✅ Спасибо, чек успешно загружен!")
    await msg.delete()

    await state.reset_state(with_data=False)
    return {"internal": internal.to_closed()}
