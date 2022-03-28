from aiogram.types import Message

from common.schemas import SelfEmployedGet, ContentType

from .interfaces import MRInternal, Service
from .keyboards import service_keyboard


async def answer(
    message: Message,
    internal: MRInternal,
    self_employed: SelfEmployedGet,
):
    text = (
        "Выбери перечь выполненных в этом месяце услуг\n"
        f"{services_to_text(internal.services)}"
    )
    await message.answer(text, reply_markup=service_keyboard(self_employed.services))
    await message.delete()
    if internal.current_message:
        await internal.current_message.delete()
        internal.set_current_message(None)


def services_to_text(services: list[Service], payout=False):
    text = ""
    for i, service in enumerate(services, 1):
        s_text = ""
        if service.type in [ContentType.INT, ContentType.PHOTOS]:
            s_text += f"<code>{i}.</code> <b>{service.name}</b> - {service.amount}"
        elif service.type == ContentType.BOOL:
            s_text += f"<code>{i}.</code> <b>{service.name}</b>"

        if payout:
            s_text += f" | {service.payout}₽\n"
        else:
            s_text += "\n"
        text += s_text
    return text
