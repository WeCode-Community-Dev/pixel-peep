import cv2
import imagehash
import numpy as np
from PIL import Image

def compute_histogram(file_path: str) -> 'np.ndarray':
    """
    Compute a normalized HSV histogram (Hue channel only) for the given image.

    Args:
        file_path (str): The path to the image file.

    Returns:
        np.ndarray: Normalized histogram of the Hue channel.
    """
    
    image = cv2.imread(file_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {file_path}")

    # Convert image from BGR (OpenCV default) to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Calculate histogram for the Hue channel (channel index 0)
    hist = cv2.calcHist([hsv_image], [0], None, [50], [0, 180])

    # Normalize the histogram to a range of 0 to 1
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    # Add a small constant to avoid zero values (useful for similarity measures)
    hist += 1e-6

    return hist

def compute_hash_val(file_path: str) -> imagehash.ImageHash:
    """
    Compute the perceptual hash (pHash) of an image using the ImageHash library.

    Args:
        file_path (str): The path to the image file.

    Returns:
        imagehash.ImageHash: The perceptual hash of the image.
    """
    try:
        # Open the image using PIL and convert to RGB to ensure consistent format
        image = Image.open(file_path).convert('RGB')
    except Exception as e:
        raise IOError(f"Unable to open image at {file_path}: {e}")

    # Compute perceptual hash
    return imagehash.phash(image)
