import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from typing import Tuple

class SSIMComparator:
    """
    Structural Similarity Index (SSIM) comparison
    Most accurate but computationally expensive
    """
    
    def __init__(self, threshold: float = 0.8, win_size: int = 7, 
                 dynamic_range: int = 255, multichannel: bool = False):
        self.threshold = threshold
        self.win_size = win_size
        self.dynamic_range = dynamic_range
        self.multichannel = multichannel
    
    def compare(self, img1_path: str, img2_path: str) -> Tuple[bool, float]:
        """
        Compare two images using SSIM
        Returns: (bool: match, float: similarity_score)
        """
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        if img1 is None or img2 is None:
            raise ValueError("Could not load one or both images")
        
        # Ensure images have same dimensions
        if img1.shape != img2.shape:
            return False, 0.0
        
        # Convert to grayscale if not multichannel
        if not self.multichannel:
            img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Compute SSIM
        score = ssim(
            img1, img2,
            win_size=self.win_size,
            data_range=self.dynamic_range,
            multichannel=self.multichannel
        )
        
        return score >= self.threshold, score