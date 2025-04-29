from django.shortcuts import render
from .models import OriginalImageModel
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Create your views here.


def upload_image_to_db(request):
    ''' upload original image into database'''

    if request.method == 'POST':
        image_data = request.FILES['image-data']

        image = OriginalImageModel(image_uploaded = image_data)
        image.save()
        return render(request,'images_upload.html', {'message':'Image successfully stored inside Db'})
    return render(request,'images_upload.html')
    

def image_similarity_upload(request):             
    return render(request, 'edited_img_upload.html')


def optimised_solution(request):
    ''' > The uploaded image is fetched and compared with all original images stored in the database.
        > Image comparison is performed pixel-by-pixel using openCV and the scikit-image library.
        > Both images are read using OpenCV.

        > The comparison based on Structural Similarity Index (SSIM), which extracts 3 key features from an image: 
          Luminance, Contrast, Structure.
        > Comparison between the two images is performed on the basis of these 3 features.

        > SSIM computes a similarity score between the two images, ranging from 0 to 1:
            > score of 1 indicates the images are identical or highly similar.
            > score of 0 indicates the images are completely different.

        > All images and their corresponding SSIM scores are stored in a list. From this list, 
          images with a similarity score of 0.9 or higher are selected.
        > Among these, the image with highest score selected. Return the Image alongwith similarity score.
 
    '''

    if request.method == 'POST':        
        duplicate_img = request.FILES['duplicate-image']
        img1 = cv2.imdecode(np.frombuffer(duplicate_img.read(), dtype= np.uint8), cv2.IMREAD_GRAYSCALE)

        # image resize
        dimension = (2500, 2500)
        img_1 = cv2.resize(img1, dimension)

        # fetch all original img from db
        original_images = OriginalImageModel.objects.all()

        score = []
        for original in original_images:
            with open(original.image_uploaded.path, 'rb') as db_img:
                img2 = cv2.imdecode(np.frombuffer(db_img.read(), dtype= np.uint8), cv2.IMREAD_GRAYSCALE)
                img_2 = cv2.resize(img2, dimension)

                ssim_score, dif = ssim(img_1, img_2, full= True)
                score.append((ssim_score, original.image_uploaded.url))

        filterd_score = [s for s in score if s[0]>= 0.9]

        if filterd_score:
            high_similarity_image = max(filterd_score, key=lambda i: i[0])
        
            return render(request, 'home_page.html', {'similarity_score':high_similarity_image[0], 'image': high_similarity_image[1]})
        
        return render(request, 'home_page.html', {'message':'Matching Image Not found'})
    
    return render(request, 'home_page.html')
    
        
            





                
                       


