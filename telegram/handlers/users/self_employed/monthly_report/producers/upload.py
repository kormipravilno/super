from datetime import datetime
import math
from pprint import pprint
from typing import Any
from pathlib import Path

from pydantic import HttpUrl

from common.schemas import SelfEmployedSchema, SelfEmployedGet, ContentType
from common.mq.engine import rpc
from common.crud import settings

from ..interfaces import (
    MonthlyReportExternal,
    MRInternal,
    Service,
    ServiceExternal,
)


async def create_folder(dt: datetime, self_employed: SelfEmployedSchema) -> dict:
    parent = await settings.get("folder_self_employed")

    month_folder = await rpc.call(
        "google.drive.create_if_not_found",
        dict(
            name=dt.strftime("%Y.%m"),
            parent_id=parent,
        ),
    )
    self_employed_folder = await rpc.call(
        "google.drive.create",
        dict(name=self_employed.full_name, parent_id=month_folder["id"]),
    )

    return self_employed_folder


async def upload_files(services: list[Service], parent) -> list[ServiceExternal]:
    folders = {
        service.name: service.value
        for service in services
        if isinstance(service.value, Path)
    }

    folders_uploaded: dict[str, dict[str, Any]] = await rpc.call(
        "google.drive.upload_all_folders",
        dict(
            folders=folders,
            parent_id=parent,
        ),
    )

    external_services = []
    for service in services:
        folder_uploaded = folders_uploaded.get(service.name)
        if folder_uploaded:
            external_service = ServiceExternal.from_internal(
                service, folder_uploaded.get("webViewLink")
            )
        else:
            external_service = ServiceExternal(**service.dict())
        external_services.append(external_service)

    return external_services


async def upload_data(external: MonthlyReportExternal):
    spreadsheet = await settings.get("spreadsheet_data")
    sheet = await settings.get("sheet_self_employed")
    schema = await rpc.call(
        "google.sheets.process.get_sheet_schema",
        dict(
            id=spreadsheet,
            sheet_name=sheet,
        ),
    )

    values = []
    external_data = external.to_flat_dict(preserve_special=True)
    for service in external.services:
        service_values = []
        data = service.to_flat_dict(preserve_special=True) | external_data
        for key in schema:
            service_values.append(data.get(key))
        values.append(service_values)

    record_data = await rpc.call(
        "google.sheets.process.append",
        dict(
            id=spreadsheet,
            sheet_name=sheet,
            values=values,
        ),
    )

    record = dict(zip(schema, record_data["values"][0]))
    return record


async def construct_doc(
    external: MonthlyReportExternal,
    self_employed: SelfEmployedGet,
    parent: str,
    path: Path,
):
    file = await rpc.call(
        "google.drive.copy",
        dict(id=self_employed.template_id, parent=parent, name="Акт"),
    )

    tables_images = await create_tables(external, file)
    await insert_images(tables_images, file)
    await replace_placeholders(external, self_employed, file)
    return await export_doc(Path(path, "Акт.pdf"), file)


async def create_tables(external: MonthlyReportExternal, file: dict):
    doc = await rpc.call("google.docs.process.get", dict(id=file["id"]))

    tables = []
    tables_images = []
    placeholders_to_delete = []

    for service in external.self_employed.services:
        if service.type == ContentType.PHOTOS:
            external_service = external.get_service(service.id)
            paragraph = await rpc.call(
                "google.docs.parse.find_paragraph",
                dict(
                    elements=doc["body"]["content"],
                    text=f"{{{{services.{service.name}.photos}}}}\n",
                ),
            )
            if external_service:
                if paragraph:
                    tables.append(
                        {
                            "paragraph": paragraph,
                            "range": {"rows": math.ceil(external_service.amount / 4)},
                        }
                    )
                    tables_images.append(
                        {
                            "offset": paragraph["startIndex"],
                            # FIXME
                            "folder": external_service.value.path.split("/")[-1],
                        }
                    )
            else:
                placeholders_to_delete.append(paragraph)

    await rpc.call(
        "google.docs.process.replace_with_tables_at",
        dict(id=file["id"], data=tables),
    )

    await rpc.call(
        "google.docs.process.delete_paragraphs",
        dict(id=file["id"], ranges=placeholders_to_delete),
    )

    return tables_images


async def insert_images(tables_images: dict, file: dict):
    doc = await rpc.call("google.docs.process.get", dict(id=file["id"]))

    images = []
    for table in tables_images:
        indexes, _ = await rpc.call(
            "google.docs.parse.find_first_table",
            dict(elements=doc["body"]["content"], offset=table["offset"]),
        )

        files = await rpc.call("google.drive.list_folder", dict(id=table["folder"]))
        unused = len(indexes) - len(files)

        for i, uploaded_file in enumerate(reversed(files), 1):
            if uploaded_file["mimeType"] == "image/jpeg":
                index = indexes[-(i + unused)]
                images.append({"image": uploaded_file, "index": index})

    pprint(images)
    await rpc.call(
        "google.docs.process.insert_images_at", dict(id=file["id"], data=images)
    )


async def replace_placeholders(
    external: MonthlyReportExternal, self_employed: SelfEmployedGet, file: dict
):
    for service in self_employed.services:
        if not external.get_service(service.id):
            external.services.append(ServiceExternal.from_value(service, value=0))

    data = external.dict()
    services = {}
    for service in external.services:
        services |= {service.name: service.dict()}

    data |= {"services": services}
    flat_data = MonthlyReportExternal.flatten_dict(data)

    pprint(flat_data)

    await rpc.call(
        "google.docs.process.replace_text", dict(id=file["id"], data=flat_data)
    )


async def export_doc(path: Path, file) -> Path:
    return await rpc.call("google.drive.export", dict(id=file["id"], file=path))


async def upload_file(path: Path, parent):
    await rpc.call(
        "google.drive.upload",
        dict(
            file=path,
            parent_id=parent,
        ),
    )
