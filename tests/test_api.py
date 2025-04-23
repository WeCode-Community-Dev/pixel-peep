import unittest
import os
from fastapi.testclient import TestClient
from imagecompare.api.web import app

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data', 'images')
        
        # Paths to test images
        cls.identical1 = os.path.join(cls.test_data_dir, 'base', 'empuran_prithvi_1.jpg')
        cls.identical2 = os.path.join(cls.test_data_dir, 'variants', 'empuran_prithvi_variant_1.jpg')
        cls.different = os.path.join(cls.test_data_dir, 'base', 'thudarum_1.png')

    def test_compare_endpoint(self):
        """Test basic comparison endpoint"""
        with open(self.identical1, 'rb') as f1, open(self.identical2, 'rb') as f2:
            response = self.client.post(
                "/compare?method=phash",
                files={"file1": f1, "file2": f2}
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["match"])
            self.assertGreaterEqual(response.json()["confidence"], 0.9)

    def test_cascading_compare(self):
        """Test the cascading comparison endpoint"""
        with open(self.identical1, 'rb') as f1, open(self.different, 'rb') as f2:
            response = self.client.post(
                "/compare/cascade",
                files={"file1": f1, "file2": f2}
            )
            self.assertEqual(response.status_code, 200)
            results = response.json()
            self.assertIn("best_match", results)
            self.assertIn("all_results", results)
            self.assertFalse(results["best_match"]["match"])

    def test_invalid_method(self):
        """Test with invalid comparison method"""
        with open(self.identical1, 'rb') as f1, open(self.identical2, 'rb') as f2:
            response = self.client.post(
                "/compare?method=invalid",
                files={"file1": f1, "file2": f2}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid method", response.json()["detail"])

    def test_missing_file(self):
        """Test with missing file upload"""
        with open(self.identical1, 'rb') as f1:
            response = self.client.post(
                "/compare?method=phash",
                files={"file1": f1}  # Missing file2
            )
            self.assertEqual(response.status_code, 422)  # Unprocessable Entity