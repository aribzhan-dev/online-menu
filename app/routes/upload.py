from fastapi import APIRouter, UploadFile, File
from app.utils.file_upload import FileUploadUtility

router = APIRouter()
upload_service = FileUploadUtility()


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    path = await upload_service.upload_image(file)

    return {
        "success": True,
        "path": path
    }