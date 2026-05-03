import io
import os
from typing import Optional

import google.generativeai as genai
from PIL import Image

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIImageService:
    """Service for AI-powered image enhancement using Google Gemini"""

    def __init__(self):
        if settings.AI_ENABLED and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"AI Image Service initialized with model: {settings.GEMINI_MODEL}")
        else:
            self.model = None
            logger.warning("AI Image Service disabled or API key not configured")

    async def enhance_food_image(self, image_path: str) -> Optional[bytes]:
        """
        Enhance food image using Gemini AI.

        Args:
            image_path: Path to the original image file

        Returns:
            Enhanced image as bytes, or None if enhancement fails

        Process:
            1. Remove or blur the background (make it clean/neutral)
            2. Enhance the plate and presentation (lighting, colors)
            3. DO NOT modify the actual food/dish
            4. Keep the composition natural and appetizing
        """
        if not self.model:
            logger.warning("AI enhancement requested but service is disabled")
            return None

        try:
            logger.info(f"Starting AI enhancement for image: {image_path}")

            # Load and validate image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None

            image = Image.open(image_path)

            # Verify it's a valid image
            image.verify()

            # Reopen after verify (verify closes the file)
            image = Image.open(image_path)

            # Prepare prompt for Gemini
            prompt = """
You are a professional food photographer AI assistant.

Task: Enhance this food image for a restaurant menu:

1. Remove or blur the background to make it clean and neutral (white or soft gradient)
2. Enhance the plate presentation with better lighting and color balance
3. Make the food look more appetizing and professional
4. DO NOT modify the actual food/dish itself - keep it authentic
5. Maintain natural composition and realistic appearance
6. Ensure the image looks suitable for a restaurant menu

Important: Return ONLY the enhanced image. Keep original dimensions and quality.
"""

            logger.info("Sending image to Gemini API for enhancement")

            # Call Gemini API
            response = self.model.generate_content([prompt, image])

            # Check if response contains image data
            if not response.parts:
                logger.error("No response parts received from Gemini API")
                return None

            # Extract enhanced image from response
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    enhanced_image_data = part.inline_data.data
                    logger.info(f"AI enhancement completed successfully, size: {len(enhanced_image_data)} bytes")
                    return enhanced_image_data

            logger.warning("No image data found in Gemini response")
            return None

        except Exception as e:
            logger.error(f"AI enhancement failed: {str(e)}", exc_info=True)
            return None

    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None and settings.AI_ENABLED


# Singleton instance
ai_image_service = AIImageService()
