import cv2
import numpy as np
from typing import Tuple

class HistogramComparator:
    """
    Color histogram-based image comparison
    Good for images with similar color distributions but different content
    """
    
    def __init__(self, threshold: float = 0.85, bins: int = 8):
        self.threshold = threshold
        self.bins = bins
    
    def compare(self, img1_path: str, img2_path: str) -> Tuple[bool, float]:
        """
        Compare two images using color histograms
        Returns: (bool: match, float: similarity_score)
        """
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        if img1 is None or img2 is None:
            raise ValueError("Could not load one or both images")
        
        # Calculate histograms
        hist1 = self._calc_histogram(img1)
        hist2 = self._calc_histogram(img2)
        
        # Compare histograms
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        return similarity >= self.threshold, similarity
    
    def _calc_histogram(self, img):
        """Calculate normalized color histogram"""
        hist = cv2.calcHist(
            [img],
            [0, 1, 2],  # Channels
            None,       # Mask
            [self.bins] * 3,  # Bins per channel
            [0, 256] * 3  # Range
        )
        return cv2.normalize(hist, hist).flatten()