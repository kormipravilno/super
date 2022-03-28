from pathlib import Path

from google.loader import client
from google.api import Drive, MimeType

from .group import DRIVE


@DRIVE.worker()
async def create(*, name: str, parent_id: str, mime_type: MimeType = MimeType.FOLDER):
    async with client as c:
        drive = Drive(c)
        response = await drive.create(parent_id, name, mime_type)
    return response


@DRIVE.worker()
async def create_if_not_found(
    *, name: str, parent_id: str, mime_type: MimeType = MimeType.FOLDER
):
    async with client as c:
        drive = Drive(c)
        response = await drive.create_if_not_found(parent_id, name, mime_type)
    return response


@DRIVE.worker()
async def upload(*, file: Path, parent_id: str):
    async with client as c:
        drive = Drive(c)
        response = await drive.upload(file, parent_id, file.name)
    return response


@DRIVE.worker()
async def upload_all(*, files: dict[str, Path], parent_id: str):
    responses = {}
    async with client as c:
        drive = Drive(c)
        for name, file in files.items():
            response = await drive.upload(file, parent_id, file.name)
            responses[name] = response
    return responses


@DRIVE.worker()
async def upload_folder(*, folder: Path, parent_id: str):
    async with client as c:
        drive = Drive(c)
        responses = []
        for path in folder.iterdir():
            if path.is_file():
                response = await drive.upload(path, parent_id, path.name)
                responses.append(response)
    return responses


@DRIVE.worker()
async def upload_all_folders(*, folders: dict[str, Path], parent_id: str):
    responses = {}
    async with client as c:
        drive = Drive(c)
        for name, folder in folders.items():
            drive_folder = await drive.create(parent_id, name)
            for path in folder.iterdir():
                if path.is_file():
                    await drive.upload(path, drive_folder["id"], path.name)
            responses[name] = drive_folder
    return responses


@DRIVE.worker()
async def list_folder(*, id: int):
    async with client as c:
        drive = Drive(c)
        return await drive.list_folder(id)


@DRIVE.worker()
async def copy(id: str, parent: str, name: str):
    async with client as c:
        drive = Drive(c)
        return await drive.copy(id, parent, name)


@DRIVE.worker()
async def export(id: str, file: Path, mime_type: MimeType = MimeType.PDF) -> Path:
    async with client as c:
        drive = Drive(c)
        await drive.export(id, file.parent, file.name, mime_type)
        return file
