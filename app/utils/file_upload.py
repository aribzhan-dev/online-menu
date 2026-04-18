import os
import uuid
import time
from datetime import datetime
from typing import Dict

from fastapi import UploadFile, HTTPException, status

ALLOWED_IMAGE_TYPES: Dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


class FileUploadUtility:
    UPLOAD_DIRECTORY = "uploads/images"
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    def __init__(self):
        os.makedirs(self.UPLOAD_DIRECTORY, exist_ok=True)

    async def upload_image(self, file: UploadFile) -> str:
        self._validate_image_type(file.content_type)
        now = datetime.now()
        folder = f"{now.year}/{now.month:02}/{now.day:02}"
        full_path = os.path.join(self.UPLOAD_DIRECTORY, folder)
        os.makedirs(full_path, exist_ok=True)
        ext = ALLOWED_IMAGE_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4().hex}_{int(time.time())}.{ext}"
        file_path = os.path.join(full_path, unique_filename)

        try:
            size = 0

            with open(file_path, "wb") as buffer:
                while True:
                    chunk = await file.read(1024 * 1024)  # 1MB
                    if not chunk:
                        break

                    size += len(chunk)

                    if size > self.MAX_FILE_SIZE_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File size exceeds {self.MAX_FILE_SIZE_MB}MB"
                        )

                    buffer.write(chunk)

        except HTTPException:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {e}"
            )
        return f"/uploads/images/{folder}/{unique_filename}"

    def _validate_image_type(self, content_type: str):
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"
            )