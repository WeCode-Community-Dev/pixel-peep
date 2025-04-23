"""
Basic usage example of ImageCompare Python API
"""
from imagecompare import compare_images, get_comparison_methods

# List available methods
print("Available methods:")
for name, desc in get_comparison_methods().items():
    print(f"- {name}: {desc}")

# Compare two images
image1 = "tests/test_data/images/base/empuran_prithvi_1.jpg"
image2 = "tests/test_data/images/variants/empuran_prithvi_variant_2.jpg"
differentImage = "tests/test_data/images/base/thudarum_1.png"

print("\nComparing images:")
match, confidence = compare_images(image1, image2, method="phash")
print(f"Result: {'MATCH' if match else 'NO MATCH'}")
print(f"Confidence: {confidence:.2f}")

print("\nComparing different images:")
match, confidence = compare_images(image1, differentImage, method="phash")
print(f"Result: {'MATCH' if match else 'NO MATCH'}")
print(f"Confidence: {confidence:.2f}")
