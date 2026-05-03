from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.utils.file_upload import FileUploadUtility
from app.services.ai_image_service import ai_image_service
from app.core.logger import get_logger
from app.core.config import settings
import os

router = APIRouter()
upload_service = FileUploadUtility()
logger = get_logger(__name__)


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image without AI enhancement.

    Returns:
        - success: Boolean indicating upload status
        - path: URL path to the uploaded image
    """
    logger.info(f"Uploading image: {file.filename}")
    path = await upload_service.upload_image(file)

    return {
        "success": True,
        "path": path
    }


@router.post("/image-with-ai")
async def upload_image_with_ai(
    file: UploadFile = File(...),
    enhance: bool = True
):
    """
    Upload image with optional AI enhancement.

    Args:
        file: Image file to upload
        enhance: Whether to apply AI enhancement (default: True)

    Returns:
        - success: Boolean indicating upload status
        - original_path: URL path to the original uploaded image
        - enhanced_path: URL path to AI-enhanced image (if enhance=True and AI is enabled)
        - ai_error: Error message if AI enhancement fails (optional)

    Process:
        1. Upload and save original image
        2. If enhance=True and AI is enabled, send to Gemini API
        3. Gemini removes background and enhances presentation
        4. Save enhanced version with "_enhanced" suffix
        5. Return both paths so admin can choose which to use
    """
    logger.info(f"Uploading image with AI enhancement: {file.filename}, enhance={enhance}")

    # 1. Save original image
    original_path = await upload_service.upload_image(file)
    logger.info(f"Original image saved: {original_path}")

    # If AI enhancement is disabled or not requested, return original only
    if not enhance or not settings.AI_ENABLED:
        logger.info("AI enhancement skipped (disabled or not requested)")
        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": None
        }

    # Check if AI service is available
    if not ai_image_service.is_available():
        logger.warning("AI service not available")
        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": None,
            "ai_error": "AI service not configured"
        }

    # 2. Enhance with AI
    try:
        # Convert URL path to file system path
        full_path = f".{original_path}"

        logger.info(f"Sending image to AI for enhancement: {full_path}")
        enhanced_data = await ai_image_service.enhance_food_image(full_path)

        if not enhanced_data:
            logger.warning("AI enhancement returned no data")
            return {
                "success": True,
                "original_path": original_path,
                "enhanced_path": None,
                "ai_error": "AI enhancement failed to generate image"
            }

        # 3. Save enhanced image
        # Create enhanced filename (e.g., abc123.jpg -> abc123_enhanced.jpg)
        path_parts = original_path.rsplit(".", 1)
        if len(path_parts) == 2:
            enhanced_path = f"{path_parts[0]}_enhanced.{path_parts[1]}"
        else:
            enhanced_path = f"{original_path}_enhanced"

        full_enhanced_path = f".{enhanced_path}"

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_enhanced_path), exist_ok=True)

        # Write enhanced image
        with open(full_enhanced_path, "wb") as f:
            f.write(enhanced_data)

        logger.info(f"Enhanced image saved: {enhanced_path}")

        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": enhanced_path
        }

    except Exception as e:
        logger.error(f"AI enhancement error: {str(e)}", exc_info=True)
        # If AI fails, still return original image
        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": None,
            "ai_error": str(e)
        }