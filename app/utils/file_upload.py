import os
import uuid
import time
from datetime import datetime
from typing import Dict

from fastapi import UploadFile, HTTPException, status
from app.core.constants import (
    ALLOWED_IMAGE_TYPES,
    MAX_FILE_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
    UPLOAD_DIRECTORY,
    FILE_CHUNK_SIZE
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class FileUploadUtility:
    def __init__(self):
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    async def upload_image(self, file: UploadFile) -> str:
        self._validate_image_type(file.content_type)
        now = datetime.now()
        folder = f"{now.year}/{now.month:02}/{now.day:02}"
        full_path = os.path.join(UPLOAD_DIRECTORY, folder)
        os.makedirs(full_path, exist_ok=True)
        ext = ALLOWED_IMAGE_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4().hex}_{int(time.time())}.{ext}"
        file_path = os.path.join(full_path, unique_filename)

        logger.info(f"Uploading image: {unique_filename}")

        try:
            size = 0

            with open(file_path, "wb") as buffer:
                while True:
                    chunk = await file.read(FILE_CHUNK_SIZE)
                    if not chunk:
                        break

                    size += len(chunk)

                    if size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"File size exceeds limit: {size} bytes")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB"
                        )

                    buffer.write(chunk)

            logger.info(f"Image uploaded successfully: {file_path} ({size} bytes)")

        except HTTPException:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}", exc_info=True)
            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {e}"
            )
        return f"/uploads/images/{folder}/{unique_filename}"

    def _validate_image_type(self, content_type: str):
        if content_type not in ALLOWED_IMAGE_TYPES:
            logger.warning(f"Invalid image type: {content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"
            )