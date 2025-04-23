import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

def normalize_for_comparison(
    img_path: Union[str, Path, np.ndarray],
    target_size: Optional[Tuple[int, int]] = (256, 256),
    normalize_method: str = "robust",
    convert_to: str = "LAB"
) -> np.ndarray:
    """
    Normalize an image for comparison by:
    1. Loading/resizing (if needed)
    2. Converting to specified color space
    3. Applying normalization
    
    Args:
        img_path: Path to image or numpy array
        target_size: Optional resize dimensions (width, height)
        normalize_method: "minmax", "zscore", or "robust" (default)
        convert_to: Color space ("BGR", "LAB", "HSV", "GRAY")
    
    Returns:
        Normalized image in float32 format (0-1 range)
    
    Raises:
        ValueError: If image cannot be loaded or invalid parameters
    """
    try:
        # Load image if path provided
        if isinstance(img_path, (str, Path)):
            img = cv2.imread(str(img_path))
            if img is None:
                raise ValueError(f"Could not load image from {img_path}")
        else:
            img = img_path.copy()
        
        # Validate image
        if len(img.shape) not in (2, 3):
            raise ValueError(f"Invalid image dimensions: {img.shape}")
        
        # Convert grayscale to BGR if needed
        if len(img.shape) == 2 or img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        # Resize if requested
        if target_size is not None:
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        
        # Convert color space
        img = _convert_color_space(img, convert_to)
        
        # Normalize channels
        img = _normalize_channels(img, normalize_method)
        
        return img.astype(np.float32)
    
    except Exception as e:
        logger.error(f"Normalization failed: {str(e)}")
        raise

def _convert_color_space(img: np.ndarray, space: str) -> np.ndarray:
    """Convert image to specified color space"""
    space = space.upper()
    if space == "BGR":
        return img
    elif space == "LAB":
        return cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    elif space == "HSV":
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    elif space == "GRAY":
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[:,:,np.newaxis]
    else:
        raise ValueError(f"Unsupported color space: {space}")

def _normalize_channels(
    img: np.ndarray, 
    method: str,
    clip: bool = True
) -> np.ndarray:
    """
    Normalize image channels using specified method
    
    Args:
        img: Input image (H,W,C)
        method: Normalization method
        clip: Whether to clip values to [0,1] range
    
    Returns:
        Normalized image in float32
    """
    img = img.astype(np.float32)
    normalized = np.zeros_like(img)
    
    for c in range(img.shape[2]):
        channel = img[:,:,c]
        
        if method == "minmax":
            min_val, max_val = np.min(channel), np.max(channel)
            if max_val - min_val > 0:
                normalized[:,:,c] = (channel - min_val) / (max_val - min_val)
        
        elif method == "zscore":
            mean, std = np.mean(channel), np.std(channel)
            if std > 0:
                normalized[:,:,c] = (channel - mean) / std
            else:
                normalized[:,:,c] = channel - mean
        
        elif method == "robust":
            lower, upper = np.percentile(channel, [1, 99])
            if upper - lower > 0:
                normalized[:,:,c] = np.clip(channel, lower, upper)
                normalized[:,:,c] = (normalized[:,:,c] - lower) / (upper - lower)
            else:
                normalized[:,:,c] = channel - lower
        
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    if clip:
        normalized = np.clip(normalized, 0, 1)
    
    return normalized