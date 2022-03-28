from enum import Enum
from pathlib import Path
from pprint import pprint

from .common import Service


class MimeType(str, Enum):
    FOLDER = "application/vnd.google-apps.folder"
    PDF = "application/pdf"


class Drive(Service, api_name="drive", api_version="v3"):
    FIELDS = "id, name, webViewLink, thumbnailLink, mimeType"

    async def get(self, id_):
        return await self.client.as_service_account(
            self.API.files.get(fileId=id_), full_res=True
        )

    async def export(self, id, path, name, mime_type: MimeType):
        Path(path).mkdir(parents=True, exist_ok=True)
        return await self.client.as_service_account(
            self.API.files.export(
                fileId=id, mimeType=mime_type.value, download_file=f"{path}/{name}"
            )
        )

    async def create_if_not_found(
        self, parent, name, mime_type: MimeType = MimeType.FOLDER
    ):
        files = await self.find(parent, name, mime_type)
        if files["files"]:
            file = files["files"][0]
        else:
            file = await self.create(parent, name, mime_type)
        return file

    async def find(self, parent, name, mime_type: MimeType = MimeType.FOLDER):
        return await self.client.as_service_account(
            self.API.files.list(
                q=f"name = '{name}' and "
                f"'{parent}' in parents "
                f"and mimeType = '{mime_type.value}'",
                fields=f"files({self.FIELDS})",
            )
        )

    async def list_folder(self, id):
        files = []
        page_token = None
        while True:
            response = await self.client.as_service_account(
                self.API.files.list(
                    q=f"'{id}' in parents",
                    fields=f"files({self.FIELDS})",
                    orderBy="createdTime",
                    pageToken=page_token,
                )
            )
            pprint(response)
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                return files

    async def copy(self, id, parent, name):
        print(id, parent, name)
        return await self.client.as_service_account(
            self.API.files.copy(
                fileId=id,
                json={"parents": [parent], "name": name},
                includePermissionsForView="published",
            )
        )

    async def create(self, parent, name, mime_type: MimeType = MimeType.FOLDER):
        return await self.client.as_service_account(
            self.API.files.create(
                json={
                    "mimeType": mime_type.value,
                    "name": name,
                    "parents": [parent],
                },
                fields=self.FIELDS,
                includePermissionsForView="published",
            )
        )

    async def upload(self, path, parent, name):
        return await self.client.as_service_account(
            self.API.files.create(
                upload_file=path,
                json={"name": name, "parents": [parent]},
                fields=self.FIELDS,
            )
        )

    async def delete(self, id):
        return await self.client.as_service_account(
            self.API.files.delete(
                fileId=id,
            )
        )
