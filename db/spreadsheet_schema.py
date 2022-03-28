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


def a():
    SPREADSHEET_SCHEMA = SpreadsheetSchema(
        sheets=[
            SheetSchema(
                name="config",
                tables=[
                    TableSchema(
                        tag="SETTINGS",
                        schema=schemas.SettingsBase,
                        model=models.Settings,
                    )
                ],
            ),
            SheetSchema(
                name="user",
                tables=[
                    TableSchema(
                        tag="COURIER",
                        schema=schemas.CourierSchema,
                        model=models.CourierModel,
                    ),
                    TableSchema(
                        tag="SELF_EMPLOYED",
                        schema=schemas.SelfEmployedSchema,
                        model=models.SelfEmployedModel,
                    ),
                    TableSchema(
                        tag="ADMIN", schema=schemas.AdminSchema, model=models.AdminModel
                    ),
                ],
            ),
            SheetSchema(
                name="chat",
                tables=[
                    TableSchema(
                        tag="REPORT_CHAT",
                        schema=schemas.ReportChatBase,
                        model=models.ReportChatModel,
                    ),
                ],
            ),
            SheetSchema(
                name="service",
                tables=[
                    TableSchema(
                        tag="SELF_EMPLOYED",
                        schema=schemas.SEServiceSchema,
                        model=models.SEServiceModel,
                    )
                ],
            ),
        ]
    )
