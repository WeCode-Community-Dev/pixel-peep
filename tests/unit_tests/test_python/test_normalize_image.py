
import cv2
import numpy as np
import os
import cv2

from src.python import normalize_for_comparison

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
img1_path = os.path.join(base_dir, 'tests', 'test_data', 'images', 'base', 'empuran_prithvi_1.jpg')
img2_path = os.path.join(base_dir, 'tests', 'test_data', 'images', 'variants', 'empuran_prithvi_variant_1.jpg')

img1 = cv2.imread(img1_path)
img2 = cv2.imread(img2_path)

if img1 is None or img2 is None:
    raise FileNotFoundError("Images not found. Check paths!")


# Normalize
img1_norm, img2_norm = normalize_for_comparison(
    img1, img2,
    target_size=(256, 256),
    normalize_method="minmax"
)

print("Normalization successful!")
print("Shape of img1_norm:", img1_norm.shape, img2_norm.shape)