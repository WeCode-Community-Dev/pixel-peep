import cv2
import numpy as np

def phash_compute(image):
    """Compute perceptual hash for an image (expects uint8 input)"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Resize to 32x32
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    
    # Convert to float32 for DCT
    float_img = np.float32(resized)
    
    # Compute DCT
    dct = cv2.dct(float_img)
    
    # Take top-left 8x8 of DCT
    dct_roi = dct[:8, :8]
    
    # Compute average (excluding DC component)
    avg = np.mean(dct_roi[1:, 1:])
    
    # Create hash
    hash_value = (dct_roi > avg).astype(int)
    
    return hash_value

def compare_phash(img1, img2):
    """
    Compare two images using pHash.
    Returns similarity score (0.0 to 1.0, where 1.0 is identical)
    """
    hash1 = phash_compute(img1)
    hash2 = phash_compute(img2)
    
    hamming_dist = np.sum(hash1 != hash2)
    max_dist = hash1.size
    similarity = 1.0 - (hamming_dist / max_dist)
    
    return similarity