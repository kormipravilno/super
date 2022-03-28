from pprint import pprint
from google.loader import client
from google.api import Docs

from .group import DOCS


PROCESS = DOCS.group("process")


@PROCESS.worker()
async def get(*, id):
    async with client as c:
        docs = Docs(c)
        return await docs.get(id)


@PROCESS.worker()
async def replace_with_tables_at(*, id: int, data: list[dict]):
    async with client as c:
        docs = Docs(c)

        requests = []
        for req in data:
            replace = [
                docs.delete_text(
                    req["paragraph"]["startIndex"],
                    req["paragraph"]["endIndex"],
                ),
                docs.insert_table(
                    req.get("range", {}).get("rows"),
                    req.get("range", {}).get("columns", 4),
                    req["paragraph"]["startIndex"],
                ),
                docs.remove_table_cell_padding(req["paragraph"]["startIndex"] + 1),
            ]
            requests.extend(replace)

        await docs.update(id, requests)


@PROCESS.worker()
async def insert_images_at(*, id: int, data: list[dict]):
    async with client as c:
        docs = Docs(c)

        requests = []
        for req in data:
            requests.append(
                docs.insert_image(req["image"]["thumbnailLink"], req["index"])
            )
        await docs.update(id, requests)


@PROCESS.worker()
async def delete_paragraphs(*, id, ranges: list[dict]):
    async with client as c:
        docs = Docs(c)

        requests = []
        for range in ranges:
            requests.append(docs.delete_text(range["startIndex"], range["endIndex"]))
        await docs.update(id, requests)


@PROCESS.worker()
async def replace_text(*, id, data: dict):
    async with client as c:
        docs = Docs(c)

        requests = []
        for key, value in data.items():
            requests.append(docs.replace_text(key, value))
        await docs.update(id, requests)
