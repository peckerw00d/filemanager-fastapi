from typing import List
from fastapi import File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import FileModel
from core.config import settings

import aiofiles


async def read_file_service(file: bytes = File(...)):
    content = file.decode("utf-8")
    lines = content.split("\n")
    return {"data": lines}


async def upload_file_service(
        session: AsyncSession,
        file: UploadFile = File(...),
):
    file.filename = file.filename.lower()

    path = f"{settings.static.media_dir}/{file.filename}"

    async with aiofiles.open(path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    file_metadata = FileModel(
        filename=file.filename,
        path=path,
        content_type=file.content_type
    )    

    session.add(file_metadata)
    await session.commit()
    await session.refresh(file_metadata)
    
    return file_metadata


async def upload_multiple_files_service(
        session: AsyncSession,
        files: List[UploadFile] = File(...),
):
    res = []
    
    for upload_file in files:
        upload_file.filename = upload_file.filename.lower()

        path = f"{settings.static.media_dir}/{upload_file.filename}"

        async with aiofiles.open(path, "wb") as out_file:
            content = await upload_file.read()
            await out_file.write(content)

        file_metadata = FileModel(
            filename=upload_file.filename,
            path=path,
            content_type=upload_file.content_type
        )    

        session.add(file_metadata)
        await session.commit()
        await session.refresh(file_metadata)
        

        res.append(file_metadata)

    return res
