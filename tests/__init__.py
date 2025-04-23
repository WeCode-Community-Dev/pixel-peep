import os
import unittest

class ImageComparisonTestCase(unittest.TestCase):
    """Base class for image comparison tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data paths"""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_data_dir = os.path.join(cls.test_dir, 'test_data', 'images', 'base')
        
        # Ensure test directory exists
        if not os.path.exists(cls.test_data_dir):
            os.makedirs(cls.test_data_dir, exist_ok=True)
    
    def get_image_path(self, filename):
        """Get full path to test image"""
        return os.path.join(self.test_data_dir, filename)