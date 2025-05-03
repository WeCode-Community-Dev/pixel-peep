import os
import uuid
import shutil
import pickle
from tkinter import Tk, filedialog
from image import compute_hash_val, compute_histogram

def train_images() -> None:
    """
    Allows the user to select and process multiple images 
    to add them as original reference images in the system.
    """
    selected_images = select_images()
    process_images(selected_images)
    print('successfully added images as original images')
    
def select_images() ->list[str]:
    """
    Select multiple images by Tkinter
    Returns:
    """
    root = Tk()
    # Tkinter window
    root.withdraw()
    file_types = [
        ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp"),
        ("All Files", "*.*")
    ]
    # Open file dialog for selecting multiple images
    selected_files = filedialog.askopenfilenames(title="Select Images", filetypes=file_types)
    return selected_files # type: ignore

def process_images(files:list[str]) -> None:
    """
    Process a list of image file paths.

    Args:
        files : A list of file paths to images that need to be processed.
    
    """
    images=[]
    for file_path in files:
        try:
            img_id=uuid.uuid4() # create unique id 
            new_path=copy_image(file_path,img_id)          
            hist=compute_histogram(file_path)
            hash_val=compute_hash_val(file_path)
            images.append({'id':img_id, 'hist':hist,'hash_val':hash_val,'file_path':new_path})
        except Exception as e:
            print(f"Failed to copy {file_path}: {e}")

    # Load existing data if the file exists
    if os.path.exists("images_details.pkl"):
        with open("images_details.pkl", "rb") as f:
            images_details = pickle.load(f)
    else:
        images_details = []

    images_details += images

    # Save the updated list back to the pickle file
    with open("images_details.pkl", "wb") as f:
        pickle.dump(images_details,f)

def copy_image(file_path: str, img_id: uuid.UUID, destination_folder: str = "original_images"):
    """
    Copy the given image to a destination folder with a new name based on image ID.

    Args:
        file_path: Path to the source image.
        img_id: Unique identifier to rename the image.
        destination_folder: Folder to copy the image into. Defaults to "original_images".

    Returns:
        destination_path: The path to the copied image or empty string.
    """
    # Create the folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    try:
        _, file_extension = os.path.splitext(file_path)
        destination_path = os.path.join(destination_folder, str(img_id)+file_extension)
        shutil.copy(file_path, destination_path)
        return destination_path
        # print(f"Copied: {file_path}")
    except Exception as e:
        print(f"Failed to copy {file_path}: {e}")
        return ''

if __name__ == "__main__":
    train_images()
