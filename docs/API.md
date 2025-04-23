# ImageCompare API Documentation

## Table of Contents
- [REST API Endpoints](#rest-api-endpoints)
- [Python API](#python-api)
- [CLI Interface](#cli-interface)
- [Error Handling](#error-handling)
- [Examples](#examples)

## REST API Endpoints

### Base URL
`http://localhost:8000` (when running locally)

### 1. Compare Two Images
`POST /compare`

**Parameters:**
- `file1`: First image file (required)
- `file2`: Second image file (required)
- `method`: Comparison method (`pixel`, `histogram`, `phash`, `ssim`)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/compare?method=phash" \
     -H "accept: application/json" \
     -F "file1=@image1.jpg" \
     -F "file2=@image2.jpg"
```

**Response:**
```json
{
  "match": true,
  "confidence": 0.92,
  "method": "phash",
  "threshold": 0.85
}
```

### 2. Cascading Comparison
`POST /compare/cascade`

**Parameters:**
- `file1`: Base image file
- `file2`: Comparison image file
- `confidence_threshold`: Minimum confidence (0.0-1.0)
- `timeout`: Max processing time in seconds

**Example Response:**
```json
{
  "best_match": {
    "method": "phash",
    "confidence": 0.92,
    "match": true
  },
  "all_results": [
    {
      "method": "pixel",
      "confidence": 0.45,
      "match": false
    },
    {
      "method": "phash",
      "confidence": 0.92,
      "match": true
    }
  ]
}
```

## Python API

### Basic Usage
```python
from imagecompare import compare_images

match, confidence = compare_images("img1.jpg", "img2.jpg", method="phash")
```

### Available Methods
```python
from imagecompare import get_comparison_methods

print(get_comparison_methods())
# Output: {'pixel': 'Fast comparison', 'phash': 'Perceptual hash', ...}
```

### Advanced Usage
```python
from imagecompare.core.comparators import SSIMComparator

comparator = SSIMComparator(threshold=0.8)
match, confidence = comparator.compare(img1_array, img2_array)
```

## CLI Interface

### Basic Comparison
```bash
imagecompare image1.jpg image2.jpg --method phash
```

### Batch Processing
```bash
imagecompare base.jpg compare*.jpg --output json > results.json
```

### Available Options
```
Options:
  -m, --method TEXT    Comparison method (pixel, histogram, phash, ssim)
  -t, --threshold FLOAT  Similarity threshold (0.0-1.0)
  -o, --output TEXT   Output format (simple, json, verbose)
```

## Error Handling

### Common Errors
| Code | Error                | Resolution                          |
|------|----------------------|-------------------------------------|
| 400  | Invalid method       | Use one of: pixel, histogram, etc. |
| 422  | Invalid file upload  | Check image file format             |
| 500  | Processing error     | Check server logs                   |

## Examples

### 1. Find duplicate images in a folder
```python
from glob import glob
from imagecompare import compare_images

images = glob("*.jpg")
for i, img1 in enumerate(images):
    for img2 in images[i+1:]:
        match, _ = compare_images(img1, img2)
        if match:
            print(f"Duplicates: {img1} and {img2}")
```

### 2. Web API with Python
```python
import requests

response = requests.post(
    "http://your-api/compare",
    files={"file1": open("img1.jpg", "rb"),
           "file2": open("img2.jpg", "rb")},
    params={"method": "phash"}
)
print(response.json())
```