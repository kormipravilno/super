from pprint import pprint
from .common import Service


class Docs(Service, api_name="docs", api_version="v1"):
    async def get(self, id):
        return await self.client.as_service_account(
            self.API.documents.get(documentId=id)
        )

    async def update(self, id, requests: list):
        if requests:
            return await self.client.as_service_account(
                self.API.documents.batchUpdate(
                    documentId=id,
                    json={"requests": requests},
                )
            )

    @staticmethod
    def replace_text(key, value):
        return {
            "replaceAllText": {
                "replaceText": value,
                "containsText": {
                    "matchCase": "true",
                    "text": f"{{{{{key}}}}}",
                },
            }
        }

    @staticmethod
    def delete_text(start, end):
        return {
            "deleteContentRange": {
                "range": {
                    "startIndex": start,
                    "endIndex": end,
                }
            }
        }

    @staticmethod
    def insert_table(rows, columns, index):
        return {
            "insertTable": {
                "rows": rows,
                "columns": columns,
                "location": {"segmentId": "", "index": index},
            }
        }

    @staticmethod
    def remove_table_cell_padding(index):
        dim = {"magnitude": 0, "unit": "PT"}
        return {
            "updateTableCellStyle": {
                "tableCellStyle": {
                    "paddingLeft": dim,
                    "paddingRight": dim,
                    "paddingTop": dim,
                    "paddingBottom": dim,
                },
                "fields": "paddingLeft,paddingRight,paddingTop,paddingBottom",
                "tableStartLocation": {
                    "segmentId": "",
                    "index": index,
                },
            }
        }

    @staticmethod
    def insert_image(uri, index):
        return {
            "insertInlineImage": {
                "uri": uri,
                "location": {"index": index},
                "objectSize": {
                    "width": {"magnitude": 120.33, "unit": "PT"},
                },
            }
        }


class DocsParser:
    @staticmethod
    def find_paragraph(elements, text):
        for value in elements:
            if "paragraph" in value:
                elements = value.get("paragraph").get("elements")
                for elem in elements:
                    text_run = elem.get("textRun")
                    if text_run:
                        if text_run.get("content") == text:
                            return elem
        return {"startIndex": None, "endIndex": None}

    @staticmethod
    def find_all(elements, startswith, endswith):
        result = []
        for value in elements:
            if "paragraph" in value:
                elements = value.get("paragraph").get("elements")
                for elem in elements:
                    text_run = elem.get("textRun")
                    if text_run:
                        text = text_run.get("content")
                        if text.startswith(startswith) and text.endswith(endswith):
                            result.append(elem)
        return result

    @staticmethod
    def find_first_table(elements, offset):
        for value in elements:
            if "table" in value:
                rows = value.get("table").get("tableRows")
                indexes = []
                if rows[0]["startIndex"] < offset:
                    continue
                for row in rows:
                    cells = row.get("tableCells")
                    pprint(cells)
                    for cell in cells:
                        paragraph = (
                            cell.get("content")[0].get("paragraph").get("elements")[0]
                        )
                        indexes.append(paragraph["startIndex"])
                return indexes, value["startIndex"]

    @staticmethod
    def text_search(
        elements: list[dict],
        startswith: str = "",
        endswith: str = "",
        contains: list[str] = [],
    ) -> list[dict]:
        if not (startswith or endswith or contains):
            raise ValueError("at least one criteria must be specified")

        matched = []
        for value in elements:
            elems = value.get("paragraph", {}).get("elements", [])
            for elem in elems:
                content = elem.get("textRun", {}).get("content", "")
                if (
                    content.startswith(startswith)
                    and content.endswith(endswith)
                    and all(x in content for x in contains)
                ):
                    matched.append(elem)
        return matched
