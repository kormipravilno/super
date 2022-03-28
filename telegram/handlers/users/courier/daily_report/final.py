from pathlib import Path
from datetime import datetime
from aiogram.types import CallbackQuery, Message, ContentTypes, ReplyKeyboardRemove
from aiogram.dispatcher.storage import FSMContext

from common.schemas import CourierSchema
from common.crud import report_chat, settings

from telegram.loader import dp, config
from telegram.filters.users import IsCourier

from .states import FinalStates
from .keyboards import proceed_final_callback, yes_no, yes, none, ready
from .interfaces import DailyReportInternal, DailyReportExternal
from .producers import upload_files, upload_data


@DailyReportInternal.register()
@dp.callback_query_handler(proceed_final_callback.filter())
async def proceed_final(call: CallbackQuery, internal: DailyReportInternal):
    dt = datetime.now(config.TIMEZONE)
    if internal.dt.date() != dt.date():
        await call.message.edit_text("Кажется, вы не успели закрыть отчет :(")
        return {"internal": internal.cleanup()}

    await call.message.answer("Открывалась ли сегодня смена?", reply_markup=yes_no)
    await call.message.delete()
    await FinalStates.shift_opened.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.shift_opened)
async def shift_opened(message: Message, internal: DailyReportInternal):
    answer = message.text
    match answer:
        case "Да":
            text = (
                "Все заказы доставлены, готов закрыть смену и инкассировать наличку.\n"
            )
            value = True
        case "Нет":
            text = "Все заказы доставлены, готов инкассировать наличку.\n"
            value = False
    text += (
        "Поблизости должен быть банкомат Альфа-банка, банка Открытие, Росбанка, "
        "Московского кредитного банка, Газпромбанка, Промсвязьбанка"
    )

    internal.data.update({"shift_opened": value})
    await message.answer(text, reply_markup=yes)
    await FinalStates.confirm.set()


@dp.message_handler(state=FinalStates.confirm, text="Да")
async def confirm_handler(message: Message):
    await FinalStates.orders.set()
    await message.answer(
        "Сколько заказов сегодня было?", reply_markup=ReplyKeyboardRemove()
    )


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.orders)
async def orders_handler(message: Message, internal: DailyReportInternal):
    orders = int(message.text)
    internal.data.update({"orders": orders})

    await message.answer("Были заказы без чека, номера?", reply_markup=none)
    await FinalStates.orders_noreceipt.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.orders_noreceipt)
async def orders_noreceipt_handler(message: Message, internal: DailyReportInternal):
    orders_noreceipt = message.text
    match orders_noreceipt:
        case "Не было":
            value = None
        case _:
            value = orders_noreceipt
    internal.data.update({"orders_noreceipt": value})

    await message.answer(
        "Какой пробег по одометру сейчас?", reply_markup=ReplyKeyboardRemove()
    )
    await FinalStates.mileage_final.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.mileage_final)
async def mileage_final_handler(message: Message, internal: DailyReportInternal):
    mileage_final = int(message.text)
    internal.data.update({"mileage_final": mileage_final})

    if internal.data.get("shift_opened"):
        text = (
            "Какая общая выручка за день?\n"
            "Посмотреть можно в приложении телефона "
            "Касса МойСклад - Смена - Общая сумма за смену"
        )
        await message.answer(text)
        await FinalStates.proceeds.set()
    else:
        internal.data.update({"proceeds": 0})
        await message.answer("Какая сумма выручки наличными?")
        await FinalStates.proceeds_cash.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.proceeds)
async def proceeds_handler(message: Message, internal: DailyReportInternal):
    proceeds = int(message.text)
    internal.data.update({"proceeds": proceeds})

    await message.answer("Какая сумма выручки наличными?")
    await FinalStates.proceeds_cash.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.proceeds_cash)
async def proceeds_cash_handler(message: Message, internal: DailyReportInternal):
    proceeds_cash = int(message.text)
    internal.data.update({"proceeds_cash": proceeds_cash})

    if internal.data.get("orders_noreceipt"):
        await message.answer("Какая сумма выручки без чека?")
        await FinalStates.cash_noreceipt.set()
    else:
        internal.data.update({"cash_noreceipt": 0})
        await message.answer(
            "Внеси выручку в банкомат и напиши сумму, принятую банкоматом"
        )
        await FinalStates.cash_atm.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.cash_noreceipt)
async def cash_noreceipt_handler(message: Message, internal: DailyReportInternal):
    cash_noreceipt = int(message.text)
    internal.data.update({"cash_noreceipt": cash_noreceipt})

    await message.answer("Внеси выручку в банкомат и напиши сумму, принятую банкоматом")
    await FinalStates.cash_atm.set()


@DailyReportInternal.register()
@dp.message_handler(state=FinalStates.cash_atm)
async def cash_atm_handler(message: Message, internal: DailyReportInternal):
    cash_atm = float(message.text)
    cash_cardtocard = internal.data.get("proceeds_cash") - cash_atm
    internal.data.update({"cash_atm": cash_atm, "cash_cardtocard": cash_cardtocard})

    await message.answer("Пришли фото чека или скрин экрана")
    await FinalStates.atm_receipt.set()


@DailyReportInternal.register()
@dp.message_handler(
    IsCourier(),
    is_media_group=False,
    content_types=ContentTypes.PHOTO,
    state=FinalStates.atm_receipt,
)
async def atm_receipt_handler(
    message: Message,
    state: FSMContext,
    internal: DailyReportInternal,
    courier: CourierSchema,
):
    photo = message.photo[-1]
    atm_receipt = await photo.download(
        destination_file=f"{internal.path}/Чек_{internal.dt.strftime('%Y_%m_%d')}"
    )
    internal.data.update({"atm_receipt": Path(atm_receipt.name)})

    if internal.data.get("cash_cardtocard"):
        await message.answer("Пришли фото чека или скрин card-to-card перевода")
        await FinalStates.cardtocard_receipt.set()
    else:
        if internal.data.get("shift_opened"):
            await message.answer(
                "Закрой смену в приложении Касса МойСклад с суммой инкассации",
                reply_markup=ready,
            )
            await FinalStates.close_shift.set()
        else:
            return await upload(internal, message, courier, state)


@DailyReportInternal.register()
@dp.message_handler(
    IsCourier(),
    is_media_group=False,
    content_types=ContentTypes.PHOTO,
    state=FinalStates.cardtocard_receipt,
)
async def cardtocard_receipt_handler(
    message: Message,
    state: FSMContext,
    internal: DailyReportInternal,
    courier: CourierSchema,
):
    photo = message.photo[-1]
    cardtocard_receipt = await photo.download(
        destination_file=f"{internal.path}/Карта-карта_чек_{internal.dt.strftime('%Y_%m_%d')}"
    )
    internal.data.update({"cardtocard_receipt": Path(cardtocard_receipt.name)})

    if internal.data.get("shift_opened"):
        await message.answer(
            "Закрой смену в приложении Касса МойСклад с суммой инкассации",
            reply_markup=ready,
        )
        await FinalStates.close_shift.set()
    else:
        return await upload(internal, message, courier, state)


@DailyReportInternal.register()
@dp.message_handler(IsCourier(), state=FinalStates.close_shift, text="Готово")
async def close_shift_handler(
    message: Message,
    state: FSMContext,
    internal: DailyReportInternal,
    courier: CourierSchema,
):
    return await upload(internal, message, courier, state)


async def upload(
    internal: DailyReportInternal,
    message: Message,
    courier: CourierSchema,
    state: FSMContext,
):
    msg = await message.answer(
        "🤔 Загружаю данные...", reply_markup=ReplyKeyboardRemove()
    )

    files_data = await upload_files(internal.data, courier)
    internal.data.update(files_data)

    external = DailyReportExternal.from_internal(internal, courier)
    record = await upload_data(external)

    await message.answer("✅ Данные успешно загружены!")
    await msg.delete()

    await notify(message, record, external)

    await state.reset_state(with_data=False)
    internal.closed = True
    return {"internal": internal.cleanup()}


async def notify(message: Message, record: dict, external: DailyReportExternal):
    external_data = {
        "courier": external.courier,
        "dt_start": external.dt_start,
        "dt_end": external.dt_end,
    }

    user_schema: str = await settings.get("courier_daily_report_user_schema")
    user_report = user_schema.format(record, **external_data)
    await message.answer(user_report)

    chat_schema: str = await settings.get("courier_daily_report_chat_schema")
    chat_report = chat_schema.format(record, **external_data)
    report_chats = await report_chat.get_all()

    for chat in report_chats:
        await dp.bot.send_message(chat.id, chat_report)
