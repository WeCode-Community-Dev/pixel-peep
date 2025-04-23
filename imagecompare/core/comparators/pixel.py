import cv2
import numpy as np
from typing import Tuple

class PixelComparator:
    """
    Fast pixel-level image comparison
    Best for detecting exact duplicates or near-identical images
    """
    
    def __init__(self, threshold: float = 0.95, resize: Tuple[int, int] = (256, 256)):
        self.threshold = threshold
        self.resize = resize
    
    def compare(self, img1_path: str, img2_path: str) -> Tuple[bool, float]:
        """
        Compare two images using pixel difference
        Returns: (bool: match, float: similarity_score)
        """
        img1 = self._preprocess(img1_path)
        img2 = self._preprocess(img2_path)
        
        if img1.shape != img2.shape:
            return False, 0.0
        
        diff = cv2.absdiff(img1, img2)
        non_zero = np.count_nonzero(diff)
        similarity = 1.0 - (non_zero / diff.size)
        
        return similarity >= self.threshold, similarity
    
    def _preprocess(self, img_path: str):
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Could not load image: {img_path}")
        if self.resize:
            img = cv2.resize(img, self.resize, interpolation=cv2.INTER_AREA)
        return img