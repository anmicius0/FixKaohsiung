import os
from src.config import PROJECT_ROOT


def _get_image_paths(subdir, prefix=None) -> list[str]:
    """Get paths to images with specified criteria from given subdirectory."""
    try:
        input_dir = os.path.join(PROJECT_ROOT, f"data/{subdir}")
        return [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith((".jpeg", ".jpg"))
            and (prefix is None or f.lower().startswith(prefix))
        ]
    except Exception as e:
        raise ValueError(f"Error retrieving paths from {subdir}: {e}")


def get_jpeg_paths() -> list[str]:
    """Retrieve paths to all JPEG images in the original data directory."""
    return _get_image_paths("original")


def get_timestamped_jpeg_paths() -> list[str]:
    """Retrieve paths to all timestamped JPEG images in the processed data directory."""
    return _get_image_paths("processed", prefix="timestamped")


def get_licence_jpeg_path() -> list[str]:
    """Retrieve paths to all licence plate JPEG images in the processed data directory."""
    return _get_image_paths("processed/detections/crops/LicensePlate")
