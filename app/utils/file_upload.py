import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException, status
from PIL import Image

class FileUploadUtility:
    UPLOAD_DIRECTORY = "uploads"
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg", "image/bmp"]
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    def __init__(self):
        os.makedirs(self.UPLOAD_DIRECTORY, exist_ok=True)

    async def upload_image(self, file: UploadFile) -> str:
        self._validate_image_type(file.content_type)
        await self._validate_file_size(file)

        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.UPLOAD_DIRECTORY, unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    buffer.write(chunk)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file: {e}")

        return file_path

    def _validate_image_type(self, content_type: str):
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Only {', '.join(self.ALLOWED_IMAGE_TYPES)} are allowed."
            )

    async def _validate_file_size(self, file: UploadFile):
        await file.seek(0, os.SEEK_END)
        file_size = file.tell()
        await file.seek(0)

        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the maximum limit of {self.MAX_FILE_SIZE_MB}MB."
            )

    def _get_file_extension(self, filename: str) -> str:
        return filename.split(".")[-1].lower()