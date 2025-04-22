import cv2
from skimage.metrics import structural_similarity as ssim
from .normalize_image import normalize_for_comparison
from .pHash import compare_phash

def normalizing_image(image_path, target_size=(256, 256)):
    """Normalize a single image (returns uint8 image)"""
    img_normalized = normalize_for_comparison(image_path, target_size=target_size)
    return img_normalized

def compare_images(img1_path, img2_path):
    """Core comparison workflow with debugging"""
    img1 = normalizing_image(img1_path)
    img2 = normalizing_image(img2_path)
    
    
    # Fast pHash check
    phash_diff = compare_phash(img1, img2)
    print(f"pHash similarity: {phash_diff:.2f}")
    if phash_diff > 0.85:
        return True
    
    # Convert to grayscale for SSIM
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Detailed SSIM check
    ssim_score = ssim(
        gray1,
        gray2,
        data_range=255.0,
        win_size=3  # Smaller window helps with different images
    )
    print(f"SSIM score: {ssim_score:.2f}")
    return ssim_score > 0.85