from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import time
import os
from imagecompare.core.comparators import (  # Changed from relative to absolute import
    PixelComparator,
    HistogramComparator,
    PHashComparator,
    SSIMComparator
)

app = FastAPI(
    title="Image Comparison API",
    description="API for comparing images using various algorithms",
    version="1.0.0"
)

COMPARISON_CASCADE = [
    ("pixel", "Fast pixel-level comparison"),
    ("histogram", "Color histogram comparison"),
    ("phash", "Perceptual hash comparison"),
    ("ssim", "Structural similarity index")
]

# Initialize comparators with default thresholds
comparators = {
    "pixel": PixelComparator(threshold=0.95),
    "histogram": HistogramComparator(threshold=0.85),
    "phash": PHashComparator(threshold=0.85),
    "ssim": SSIMComparator(threshold=0.8)
}

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to temporary location"""
    try:
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload_file.file.read())
            return tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        upload_file.file.close()

@app.post("/compare/cascade")
async def cascading_compare(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    confidence_threshold: float = 0.85,
    timeout: float = 5.0
) -> JSONResponse:
    """
    Compare images using cascading fallback approach (fastest to most accurate)
    
    Parameters:
    - file1: First image file
    - file2: Second image file
    - confidence_threshold: Minimum confidence to consider a match (0.0-1.0)
    - timeout: Maximum time to spend on comparison (seconds)
    
    Returns:
    - JSON with best comparison result and method used
    """
    try:
        # Save uploaded files
        path1 = save_upload_file(file1)
        path2 = save_upload_file(file2)
        
        start_time = time.time()
        results = []
        
        for method, description in COMPARISON_CASCADE:
            if time.time() - start_time > timeout:
                break
                
            try:
                comparator = comparators[method]
                is_match, confidence = comparator.compare(path1, path2)
                
                results.append({
                    "method": method,
                    "description": description,
                    "match": is_match,
                    "confidence": float(confidence),
                    "threshold": comparator.threshold,
                    "time_taken": time.time() - start_time
                })
                
                # Early exit if we found a confident match
                if confidence >= confidence_threshold:
                    break
                    
            except Exception as e:
                # Log but continue to next method
                print(f"Method {method} failed: {str(e)}")
                continue
        
        # Clean up files
        os.unlink(path1)
        os.unlink(path2)
        
        if not results:
            raise HTTPException(
                status_code=500,
                detail="All comparison methods failed"
            )
        
        # Select the best result (highest confidence that meets threshold)
        best_result = max(
            results, 
            key=lambda x: x["confidence"] if x["confidence"] >= confidence_threshold else -1
        )
        
        return JSONResponse({
            "best_match": best_result,
            "all_results": results,
            "timeout_reached": time.time() - start_time >= timeout
        })
        
    except Exception as e:
        # Clean up if files were created
        if 'path1' in locals() and os.path.exists(path1):
            os.unlink(path1)
        if 'path2' in locals() and os.path.exists(path2):
            os.unlink(path2)
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )

@app.post("/compare")
async def compare_images(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    method: Optional[str] = "phash"
) -> JSONResponse:
    """
    Compare two images using specified method
    
    Parameters:
    - file1: First image file
    - file2: Second image file
    - method: Comparison method (pixel, histogram, phash, ssim)
    
    Returns:
    - JSON with comparison result and confidence score
    """
    if method not in comparators:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method. Choose from: {', '.join(comparators.keys())}"
        )
    
    try:
        # Save uploaded files to temp locations
        path1 = save_upload_file(file1)
        path2 = save_upload_file(file2)
        
        # Get the selected comparator
        comparator = comparators[method]
        
        # Perform comparison
        is_match, confidence = comparator.compare(path1, path2)
        
        # Clean up temp files
        os.unlink(path1)
        os.unlink(path2)
        
        return JSONResponse({
            "match": is_match,
            "confidence": float(confidence),
            "method": method,
            "threshold": comparator.threshold
        })
        
    except Exception as e:
        # Clean up if files were created
        if 'path1' in locals() and os.path.exists(path1):
            os.unlink(path1)
        if 'path2' in locals() and os.path.exists(path2):
            os.unlink(path2)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare/batch")
async def batch_compare(
    base_image: UploadFile = File(...),
    compare_images: List[UploadFile] = File(...),
    method: Optional[str] = "phash"
) -> JSONResponse:
    """
    Compare a base image against multiple images
    
    Parameters:
    - base_image: Reference image
    - compare_images: List of images to compare against
    - method: Comparison method
    
    Returns:
    - List of comparison results for each image
    """
    if method not in comparators:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method. Choose from: {', '.join(comparators.keys())}"
        )
    
    try:
        # Save base image
        base_path = save_upload_file(base_image)
        comparator = comparators[method]
        results = []
        
        for img in compare_images:
            # Save each comparison image
            compare_path = save_upload_file(img)
            
            # Perform comparison
            is_match, confidence = comparator.compare(base_path, compare_path)
            
            results.append({
                "filename": img.filename,
                "match": is_match,
                "confidence": float(confidence)
            })
            
            # Clean up
            os.unlink(compare_path)
        
        # Clean up base image
        os.unlink(base_path)
        
        return JSONResponse({
            "method": method,
            "threshold": comparator.threshold,
            "results": results
        })
        
    except Exception as e:
        # Clean up any remaining files
        if 'base_path' in locals() and os.path.exists(base_path):
            os.unlink(base_path)
        if 'compare_path' in locals() and os.path.exists(compare_path):
            os.unlink(compare_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/methods")
async def list_methods() -> JSONResponse:
    """List available comparison methods"""
    methods_info = []
    for name, comparator in comparators.items():
        methods_info.append({
            "name": name,
            "description": comparator.__doc__,
            "threshold": comparator.threshold
        })
    return JSONResponse({"methods": methods_info})