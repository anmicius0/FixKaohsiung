import os
from PIL import Image
import shutil



def save_img(filename: str, image: Image.Image) -> str:
    """
    Save the processed image to the data/processed directory.

    Args:
        filename (str): Name of the file to save
        image (Image.Image): PIL Image object to save

    Returns:
        str: Path to the saved file
    """
    try:
        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{filename}.jpeg")
        image.save(output_path)

        return output_path
    except Exception as e:
        raise ValueError(f"save_img() error: {e}")


def clear_IO() -> None:
    """Clear the folders."""
    directories = ["data/processed", "data/original"]
    for directory in directories:
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory, exist_ok=True)
