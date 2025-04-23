import cv2
import numpy as np
from typing import Tuple

class PHashComparator:
    """
    Perceptual hash (pHash) image comparison
    Robust against resizing, format changes, and minor modifications
    """
    
    def __init__(self, threshold: float = 0.85, hash_size: int = 8, highfreq_factor: int = 4):
        self.threshold = threshold
        self.hash_size = hash_size
        self.highfreq_factor = highfreq_factor
    
    def compare(self, img1_path: str, img2_path: str) -> Tuple[bool, float]:
        """
        Compare two images using perceptual hashing
        Returns: (bool: match, float: similarity_score)
        """
        hash1 = self._calculate_phash(img1_path)
        hash2 = self._calculate_phash(img2_path)
        
        # Calculate Hamming distance
        hamming_dist = np.count_nonzero(hash1 != hash2)
        similarity = 1.0 - (hamming_dist / len(hash1))
        
        return similarity >= self.threshold, similarity
    
    def _calculate_phash(self, img_path: str):
        """Compute perceptual hash for an image"""
        # Read and preprocess image
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not load image: {img_path}")
        
        # Resize and compute DCT
        img_size = self.hash_size * self.highfreq_factor
        img_resized = cv2.resize(img, (img_size, img_size), interpolation=cv2.INTER_AREA)
        dct = cv2.dct(np.float32(img_resized))
        
        # Reduce DCT (keep top-left hash_size x hash_size)
        dct_reduced = dct[:self.hash_size, :self.hash_size]
        
        # Compute hash (1 where > median, else 0)
        median = np.median(dct_reduced)
        return (dct_reduced > median).flatten().astype(int)