import cv2
import numpy as np
from skimage.exposure import match_histograms  # type: ignore # Install with: pip install scikit-image

def normalize_for_comparison(img1, img2, target_size=(256, 256), normalize_method="minmax"):
    """
    Normalizes two images for comparison by:
    1. Resizing to a common size (optional).
    2. Converting to LAB color space (perceptual uniformity).
    3. Applying robust normalization.
    4. (Optional) Histogram matching.
    
    Args:
        img1, img2: Input images (can be different sizes/color spaces).
        target_size: Resize images to this (width, height). Set to `None` to disable.
        normalize_method: "minmax" (default), "zscore", or "robust".
    
    Returns:
        img1_normalized, img2_normalized: Ready for comparison (e.g., SSIM, MSE).
    """
    # --- Step 1: Resize to common size (if needed) ---
    if target_size is not None:
        img1 = cv2.resize(img1, target_size, interpolation=cv2.INTER_LANCZOS4)
        img2 = cv2.resize(img2, target_size, interpolation=cv2.INTER_LANCZOS4)
    
    # --- Step 2: Convert to LAB color space (for perceptual uniformity) ---
    img1_lab = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB)
    img2_lab = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)
    
    # --- Step 3: Normalize each channel independently ---
    def normalize_channel(channel, method):
        channel = channel.astype(np.float32)
        if method == "minmax":
            min_val, max_val = np.min(channel), np.max(channel)
            if max_val - min_val == 0:
                return np.zeros_like(channel)
            return (channel - min_val) / (max_val - min_val)
        elif method == "zscore":
            mean, std = np.mean(channel), np.std(channel)
            if std == 0:
                std = 1.0
            return (channel - mean) / std
        elif method == "robust":
            lower, upper = np.percentile(channel, 1), np.percentile(channel, 99)
            channel = np.clip(channel, lower, upper)
            return (channel - lower) / (upper - lower)
    
    # Normalize each LAB channel
    for i in range(3):  # L, A, B channels
        img1_lab[..., i] = normalize_channel(img1_lab[..., i], normalize_method)
        img2_lab[..., i] = normalize_channel(img2_lab[..., i], normalize_method)
    
    # --- Step 4 (Optional): Histogram matching (aligns brightness/contrast) ---
    img2_lab_matched = match_histograms(img2_lab, img1_lab, channel_axis=-1)
    
    # Convert back to BGR for OpenCV compatibility (optional)
    img1_normalized = cv2.cvtColor(img1_lab, cv2.COLOR_LAB2BGR)
    img2_normalized = cv2.cvtColor(img2_lab_matched, cv2.COLOR_LAB2BGR)
    
    return img1_normalized, img2_normalized