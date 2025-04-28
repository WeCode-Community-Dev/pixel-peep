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
    cv2_images=[]
    file_sizes=[]
    for image in images:
        if not is_allowed_file(image.filename):
            raise HTTPException(status_code=400, detail=f"File '{image.filename}' is not allowed. SVG files are blocked.")
    
        img,file_size=read_image(image)
        cv2_images.append(img)
        file_sizes.append(file_size)

        histograms.append(compute_histogram(img))
    com_mtx=create_comparison_matrix(histograms)
    groups=group_images(com_mtx)
    originals=set()
    for group in groups:
        original=find_original(cv2_images,group,com_mtx,file_sizes)
        originals.add(original)

    return groups,originals
    
    
def read_image(upload_file: UploadFile):
    """Convert UploadFile to OpenCV image (numpy array)."""
    image_bytes = upload_file.file.read()
    file_size = len(image_bytes)

    # Create a NumPy array from the raw image bytes
    np_array = np.frombuffer(image_bytes, np.uint8)

    # Decode the NumPy array into an OpenCV image in BGR color format
    image=cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    return image ,file_size

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

def find_original(images, group,com_matrix,file_sizes):
    scores=[]
    for i in group:
        image=images[i]

        sharp_score=compute_sharpness(image)

        size_score=file_sizes[i]*0.01

        resolution=image.shape[0]*image.shape[1]*0.001

        similarity_score=compute_similarity(i,group,com_matrix)

        score=similarity_score+sharp_score+resolution+size_score
        scores.append({i:score})
        print(i,sharp_score,size_score,resolution,similarity_score)

    key=max_score(scores)

    print(key)
    return key
def max_score(scores):
    max_score = float('-inf')
    max_key = None

    for score_dict in scores:
        for key, value in score_dict.items():
            if value > max_score:
                max_score = value
                max_key = key
    return max_key
    
        
    

def compute_similarity(index,group,com_matrix):
    total_similarity=0
    for i in group:
        total_similarity+=com_matrix[index][i]
    return total_similarity
        

def compute_sharpness(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()
