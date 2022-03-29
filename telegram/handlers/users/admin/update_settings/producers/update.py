from common.crud import purge
from db.spreadsheet_schema import SPREADSHEET_SCHEMA

from common.mq.engine import rpc

from telegram.loader import config


async def update():
    await purge()

    settings_data = await rpc.call(
        "google.sheets.process.get", dict(id=config.SPREADSHEET)
    )
    settings = await rpc.call(
        "google.sheets.parse.spreadsheet", dict(data=settings_data)
    )

    for sheet in SPREADSHEET_SCHEMA.sheets:
        sheet_data = settings.get(sheet.name)
        for table in sheet.tables:
            rows = await rpc.call(
                "google.sheets.parse.table", dict(tag=table.tag, rows=sheet_data)
            )
            await table.crud.raw_create_all(rows)
