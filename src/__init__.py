
import numpy as np
import os
import cv2
from python import compare_images
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
img1_path = os.path.join(base_dir, 'tests', 'test_data', 'images', 'base', 'empuran_prithvi_1.jpg')
img2_path = os.path.join(base_dir, 'tests', 'test_data', 'images', 'variants', 'empuran_prithvi_variant_3.jpg')

response = compare_images(img1_path, img2_path)

print("Compared successful!")
print("Result:", response)