import cv2 # type: ignore
import numpy as np # type: ignore
from fastapi import HTTPException, UploadFile
# from PIL import Image # type: ignore
from services.graph import Graph

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'webp', 'tiff', 'gif'}

def is_allowed_file(filename: str | None) -> bool:
    if filename:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return False

async def img_classification(images:list[UploadFile]):
    histograms=[]
    for image in images:
        if not is_allowed_file(image.filename):
            raise HTTPException(status_code=400, detail=f"File '{image.filename}' is not allowed. SVG files are blocked.")
    
        img=read_image(image)
        histograms.append(compute_histogram(img))
    com_mtx=create_comparison_matrix(histograms)
    groups=group_images(com_mtx)
    return groups

    
def read_image(upload_file: UploadFile):
    """Convert UploadFile to OpenCV image (numpy array)."""
    image_bytes = upload_file.file.read()
    # Create a NumPy array from the raw image bytes
    np_array = np.frombuffer(image_bytes, np.uint8)

    # Decode the NumPy array into an OpenCV image in BGR color format
    return cv2.imdecode(np_array, cv2.IMREAD_COLOR)

def compute_histogram(image):
    """Compute HSV histogram for the image."""

    #convert image from BGR to HSV color format
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #calculate histogram for the Hue channel
    hist = cv2.calcHist([hsv], [0], None, [50], [0, 180]) 
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    hist += 1e-6 # Add a small value to the histograms to avoid zero values
    return hist

def compare_histograms(hist1, hist2):
    """Compare two histograms using multiple methods."""

    # if value near to 1 the images are similar
    correlation = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)) 

    # if is smaller the images are similar
    chi_sq_1 = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
    chi_sq_2 = cv2.compareHist(hist2, hist1, cv2.HISTCMP_CHISQR)
    chi_square_final = (chi_sq_1 + chi_sq_2) / 2
    
    # if value near to 1 the images are similar
    intersection = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT))/float(cv2.compareHist(hist1, hist1, cv2.HISTCMP_INTERSECT))
    
    # if value near to 0 the images are similar
    bhattacharyya = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA))

    final_similarity=(correlation+intersection + (1-bhattacharyya) + (1/(1+chi_square_final * 0.1)))/4

    return final_similarity

def create_comparison_matrix(histograms):
    n = len(histograms)
    comparison_matrix = np.zeros((n, n))
    # Fill the matrix with similarity scores
    for i in range(n):
        for j in range(n):
            score=compare_histograms(histograms[i],histograms[j])
            comparison_matrix[i][j]=score
    return comparison_matrix

def group_images(matrix):
    # Set your similarity threshold
    threshold = 0.75

    n=len(matrix)
    graph=Graph()
    for i in range(n):
        graph.add_node(i)
        for j in range(n):
            if matrix[i][j]>=threshold and i!=j:
                graph.add_edge(i,j)

    groups=graph.get_connected_components()

    return groups