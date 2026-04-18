import os
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.core.security import check_role
from app.core.enums import UserRole

router = APIRouter(dependencies=[Depends(check_role([UserRole.COMPANY]))])

UPLOAD_DIRECTORY = "./uploads"


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is not an image.")

    try:
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        return {"filename": file.filename, "path": f"/static/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not upload file: {e}")