import os
from io import BytesIO
from datetime import datetime
from typing import List, Union

import requests
from PIL import Image, ImageDraw, ImageFont, ExifTags
from paddleocr import PaddleOCR
from ultralytics import YOLO

from src.config import INPUT_DIR, PROCESSED_DIR, FONT_FILE
from src.data_handling.input import get_jpeg_paths, get_licence_jpeg_path
from src.data_handling.output import save_img
from src.utils.ui import status_print, StatusLevel

# Constants
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"
FONT_SIZE = 120
TEXT_MARGIN = 120
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".heic", ".heif")
JPEG_EXTENSION = ".jpeg"
JPEG_QUALITY = 95
ORIENTATION_TAG = 274


def _convert_to_jpeg() -> None:
    """Converts images to JPEG format, preserving EXIF data and applying rotation."""
    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
            continue

        file_path = os.path.join(INPUT_DIR, filename)
        try:
            with Image.open(file_path) as img:
                # Apply EXIF rotation if needed
                if hasattr(img, "_getexif") and img._getexif():
                    exif = img._getexif()
                    if exif and ORIENTATION_TAG in exif:
                        rotation = {3: 180, 6: 270, 8: 90}.get(exif[ORIENTATION_TAG])
                        if rotation:
                            img = img.rotate(rotation, expand=True)

                # Convert to RGB if needed and resize
                img = img.convert("RGB") if img.mode != "RGB" else img
                img = img.resize((int(img.width * 0.3), int(img.height * 0.3)))

                # Save as JPEG with EXIF
                output_path = os.path.join(
                    INPUT_DIR, f"{os.path.splitext(filename)[0]}{JPEG_EXTENSION}"
                )
                img.save(
                    output_path, "JPEG", quality=JPEG_QUALITY, exif=img.info.get("exif")
                )

                # Remove original if different from output
                if file_path != output_path:
                    os.remove(file_path)
        except Exception as e:
            raise ValueError(f"_convert_to_jpeg(): File={filename}: {e}")


def _add_timestamp(image: Image.Image, text: str) -> Image.Image:
    """Adds timestamp text to the image with a background."""
    try:
        image_copy = image.copy()
        original_exif = image.info.get("exif")

        # Get font (fallback to default if needed)
        try:
            font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
        except (IOError, OSError):
            font = ImageFont.load_default()
            if hasattr(font, "size"):
                font = font.font_variant(size=FONT_SIZE)

        # Draw text with outline
        draw = ImageDraw.Draw(image_copy)
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
        text_x = image_copy.width - text_width - TEXT_MARGIN
        text_y = image_copy.height - text_height - TEXT_MARGIN

        # Add black outline then white text
        for dx, dy in [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
        ]:
            draw.text((text_x + dx * 5, text_y + dy * 5), text, font=font, fill="black")
        draw.text((text_x, text_y), text, font=font, fill="white")

        image_copy.info["exif"] = original_exif
        return image_copy
    except Exception as e:
        raise ValueError(f"_add_timestamp(): {e}")


def get_datetime(file_path: str) -> str:
    """Extracts timestamp from image EXIF data or file metadata."""
    try:
        with Image.open(file_path) as img:
            # Try to extract datetime from EXIF
            exif = img._getexif() or {}
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) in (
                    "DateTimeOriginal",
                    "CreateDate",
                    "DateTimeDigitized",
                    "DateTime",
                ):
                    try:
                        return datetime.strptime(
                            str(value), "%Y:%m:%d %H:%M:%S"
                        ).strftime(TIMESTAMP_FORMAT)
                    except ValueError:
                        pass

            # Fallback to file metadata
            file_time = (
                os.path.getctime(file_path)
                if os.name == "nt"
                else os.path.getmtime(file_path)
            )
            return datetime.fromtimestamp(file_time).strftime(TIMESTAMP_FORMAT)
    except Exception as e:
        raise ValueError(f"get_datetime(): File={file_path}: {e}")


def licence_recognition() -> Union[List[str], None]:
    """Detect and recognize licence plate from image."""
    try:
        # Clean previous results
        img_path = get_jpeg_paths()[0]
        model = YOLO("assets/models/yolo12m_licence.onnx", task="detect", verbose=False)
        model.predict(
            img_path,
            project=PROCESSED_DIR,
            name="detections",
            conf=0.4,
            save_crop=True,
            exist_ok=True,
        )

        # Licence recognition
        crop_path = get_licence_jpeg_path()[0]
        print(crop_path)

        # Use the ocr function directly with the file path as a local source
        text = ocr(crop_path)
        if not text:
            return None

        # Extract and filter text - only keep digits and uppercase letters
        text = "".join(char for char in text if char.isdigit() or char.isupper())

        # Check format patterns
        if len(text) == 7 and text[:3].isalpha() and text[3:].isdigit():
            return [text[:3], text[3:]]
        if len(text) == 6 and (text[:4].isdigit() or text[2:].isdigit()):
            return [
                text[: 4 if text[:4].isdigit() else 2],
                text[4 if text[:4].isdigit() else 2 :],
            ]
        return None
    except Exception as e:
        return None


def ocr(url_or_path: str) -> str:
    """Extract text from captcha image URL or local file path."""
    try:
        if url_or_path.startswith("http"):
            response = requests.get(url_or_path, timeout=10)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            temp_path = save_img("captcha", img)
            image_path = temp_path
        else:
            # Directly use the local file path
            image_path = url_or_path

        best_text = None
        max_conf = 0

        for line in PaddleOCR(lang="en").ocr(image_path):
            for detection in line:
                text, conf = detection[1]
                filtered_text = "".join(c for c in text if c.isdigit() or c.isupper())
                if (len(filtered_text) >= 4) and conf > max_conf:
                    max_conf = conf
                    best_text = filtered_text

        return best_text
    except Exception as e:
        raise ValueError(f"ocr(): Source={url_or_path}: {e}")


def preprocess_img() -> None:
    """Adds timestamps to JPEG images in the input directory."""
    status_print("Processing images...", StatusLevel.INFO)

    # Convert to JPEG format
    _convert_to_jpeg()

    # Add timestamp to each image
    jpeg_paths = get_jpeg_paths()
    for i, img_path in enumerate(jpeg_paths):
        try:
            with Image.open(img_path) as img:
                time_stamp = get_datetime(img_path)
                save_img(f"timestamped_{i}", _add_timestamp(img, time_stamp))
        except Exception as e:
            status_print(f"Error processing image {img_path}: {e}", StatusLevel.ERROR)
            raise ValueError(f"preprocess_img(): Image Path={img_path}: {e}")

    status_print(f"Processed {len(jpeg_paths)} images", StatusLevel.SUCCESS)
