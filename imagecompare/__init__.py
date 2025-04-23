"""
ImageCompare - A versatile image comparison toolkit
"""

from pathlib import Path
from typing import Union, Tuple, Dict
from .core.comparators import (
    PixelComparator,
    HistogramComparator,
    PHashComparator,
    SSIMComparator
)
from .core.preprocessing import normalize_for_comparison

# Initialize default comparators
_DEFAULT_COMPARATORS = {
    "pixel": PixelComparator(threshold=0.95),
    "histogram": HistogramComparator(threshold=0.85),
    "phash": PHashComparator(threshold=0.85),
    "ssim": SSIMComparator(threshold=0.8)
}

def compare_images(
    image1: Union[str, Path],
    image2: Union[str, Path],
    method: str = "phash",
    **kwargs
) -> Tuple[bool, float]:
    """
    Compare two images using specified method
    
    Args:
        image1: Path to first image
        image2: Path to second image
        method: Comparison method (pixel, histogram, phash, ssim)
        **kwargs: Additional comparator-specific parameters
    
    Returns:
        Tuple of (match: bool, confidence: float)
    
    Example:
        >>> from imagecompare import compare_images
        >>> match, confidence = compare_images("img1.jpg", "img2.jpg", method="phash")
        >>> print(f"Match: {match}, Confidence: {confidence:.2f}")
    """
    if method not in _DEFAULT_COMPARATORS:
        raise ValueError(
            f"Invalid method '{method}'. Available: {list(_DEFAULT_COMPARATORS.keys())}"
        )
    
    comparator = _DEFAULT_COMPARATORS[method]
    
    return comparator.compare(str(image1), str(image2))

def get_comparison_methods() -> Dict[str, str]:
    """
    Get available comparison methods with descriptions
    
    Returns:
        Dictionary of method names to descriptions
    """
    return {
        "pixel": "Fast pixel-level comparison (strict)",
        "histogram": "Color distribution comparison",
        "phash": "Perceptual hash (balanced speed/accuracy)",
        "ssim": "Structural Similarity (most accurate but slow)"
    }