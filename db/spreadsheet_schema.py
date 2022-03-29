from pydantic import BaseModel

import common.crud as crud


class TableSchema(BaseModel):
    tag: str
    crud: crud.CRUDBase

    class Config:
        arbitrary_types_allowed = True


class SheetSchema(BaseModel):
    name: str
    tables: list[TableSchema]


class SpreadsheetSchema(BaseModel):
    sheets: list[SheetSchema]


SPREADSHEET_SCHEMA = SpreadsheetSchema(
    sheets=[
        SheetSchema(
            name="config",
            tables=[
                TableSchema(tag="SETTINGS", crud=crud.settings),
            ],
        ),
        SheetSchema(
            name="user",
            tables=[
                TableSchema(tag="ADMIN", crud=crud.admin),
                TableSchema(tag="COURIER", crud=crud.courier),
                TableSchema(tag="SELF_EMPLOYED", crud=crud.self_employed),
            ],
        ),
        SheetSchema(
            name="chat",
            tables=[
                TableSchema(tag="REPORT_CHAT", crud=crud.report_chat),
            ],
        ),
        SheetSchema(
            name="service",
            tables=[TableSchema(tag="SELF_EMPLOYED", crud=crud.se_service)],
        ),
    ]
)
