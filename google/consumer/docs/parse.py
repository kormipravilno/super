from google.api import DocsParser

from .group import DOCS


PARSE = DOCS.group("parse")


@PARSE.worker()
async def find_paragraph(*, elements, text: str):
    return DocsParser.find_paragraph(elements, text)


@PARSE.worker()
async def find_first_table(*, elements, offset: int):
    return DocsParser.find_first_table(elements, offset)


@PARSE.worker()
async def text_search(
    *,
    elements,
    startswith: str = "",
    endswith: str = "",
    contains: list[str] = [],
):
    return DocsParser.text_search(elements, startswith, endswith, contains)
