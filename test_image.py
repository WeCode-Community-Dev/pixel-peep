import cv2 
import pickle
import imagehash
import numpy as np
from tkinter import Tk, filedialog
from image import compute_hash_val, compute_histogram

def test_image() -> None:
    """
    Handles the image selection and processing workflow.
    """
    selected_image = select_image()

    if selected_image:
        process_image(selected_image) 
    else:
        print("No image selected.")
    
def select_image() -> str:
    """
    Select an image by using Tkinter
    Returns:
        selected_file(str):The full file path of selected image or an empty string if no image is selected
    """
    root = Tk()
    # Tkinter window
    root.withdraw()
    file_types = [
        ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp"),
        ("All Files", "*.*")
    ]

    # Open the file dialog
    selected_file = filedialog.askopenfilename(title="Select Images", filetypes=file_types)
    return selected_file

def process_image(file_path: str) -> None:
    """
    Process a given image by computing its histogram and perceptual hash,
    finding the most similar image from the images_details.pkl file, and displaying the result.

    Args:
        file_path (str): Path to the image to be processed.
    """    
    try:  
        # 1. Extract image features   
        hist = compute_histogram(file_path)
        hash_val = compute_hash_val(file_path)

        # 2. find the most similar image
        matched_image_path,score = find_similar_image(hist, hash_val)

        # 3.display original image and message
        show_result(matched_image_path, score)
        
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

def find_similar_image(hist: 'np.ndarray' ,hash_val: imagehash.ImageHash) -> tuple[str,float]:
    '''
    find out the original image from the images_details.pkl file
    Args:
        hist: Normalized histogram of the Hue channel.
        hash_val: The perceptual hash of the image.
    Returns:
        [image_path, max_score]: Path to the most similar image and its similarity score.
    '''

    # open images_details.pkl
    with open("images_details.pkl", "rb") as f:
        images_details = pickle.load(f)

    max_score=0
    image_path=''
    for image in images_details:
        score=compare_histograms(hist,image['hist'])
        h_dist=compute_hash_dist(hash_val,image['hash_val'])

        score += 1/ (1+h_dist)
        if score>max_score:
            max_score=score
            image_path=image['file_path']

    return image_path,max_score

def compare_histograms(hist1: 'np.ndarray', hist2: 'np.ndarray') -> float:
    """
    Compare two histograms using multiple methods.
    Args:
        hist1: Normalized histogram of the Hue channel of testing image.
        hist2: Normalized histogram of the Hue channel.
    Returns:
        final_similarity: Similarity score between the two histograms.
               Higher value means more similar (max 1.0 if identical).  
    """

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

def compute_hash_dist(hash_value1: imagehash.ImageHash,hash_value2: imagehash.ImageHash) -> int:
    """
    Compute the Hamming distance between two perceptual hashes.

    Args:
        hash_value1 : Hash of the first image.
        hash_value2 : Hash of the second image.

    Returns:
        h_score: Hamming distance between the two hashes.
             Lower value means higher similarity.
    """
    h_score=hash_value1-hash_value2
    return h_score

def show_result(image_path:str,score:float):
    """
    Display the matched image with an informational message if the similarity score is above threshold.

    Args:
        image_path : Path to the image to be displayed.
        score : Similarity score between the selected and matching image.
    """
    THRESHOLD=0.75

    if score<THRESHOLD:
        print('There is not a matching image in our training set')
        return
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image {image_path}.")
        return
    
    screen_res = 800, 600  # or get dynamically
    scale_width = screen_res[0] / image.shape[1]
    scale_height = screen_res[1] / image.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(image.shape[1] * scale)
    window_height = int(image.shape[0] * scale)
    resized_image = cv2.resize(image, (window_width, window_height)) 

    message = 'Your given image is original' if score == 2.0 else 'Your given image is matching with this image'

    text_height = 50  
    image_with_text = cv2.copyMakeBorder(resized_image, 0, text_height, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))  # White border

    # Position for the message
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 0, 0)  # Black color for the message
    thickness = 2

    # Calculate message size for centering
    (text_width, text_height), _ = cv2.getTextSize(message, font, font_scale, thickness)
    text_x = (image_with_text.shape[1] - text_width) // 2
    text_y = image_with_text.shape[0] - 10  # 10 pixels above the bottom

    # Put message on the image
    cv2.putText(image_with_text, message, (text_x, text_y), font, font_scale, color, thickness)

    cv2.imshow("The original Image", image_with_text)
    cv2.waitKey(0)
    cv2.destroyAllWindows()  

if __name__ == "__main__":
    test_image()
