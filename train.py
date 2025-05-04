import os
import torch
import numpy as np
from PIL import Image
from torchvision import models, transforms
from sklearn.metrics.pairwise import cosine_similarity

# Load pretrained ResNet50 and remove classifier
resnet = models.resnet50(pretrained=True)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])  # Remove layer because it is not needed (last layers) only needs features//classifier
resnet.eval()
orginal_folder = r"C:\\Users\\LENOVO\\Documents\\PROJECTS\\pixel-peep\\images\\ originals"
# Image preprocessing for ResNet50
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    
])

def get_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = resnet(image).squeeze().numpy()
    return embedding.reshape(1, -1)

# Load all original embeddings
def load_original_embeddings(folder_path):
    embeddings = []
    filenames = []
    for file in os.listdir(folder_path):
        if file.lower().endswith((".jpg", ".png")):
            path = os.path.join(folder_path, file)
            emb = get_embedding(path)
            embeddings.append(emb)
            filenames.append(file)
    return np.vstack(embeddings), filenames

original_folder=r"C:\\Users\\LENOVO\\Documents\\PROJECTS\\pixel-peep\\images\\originals"
originals, names = load_original_embeddings(original_folder)

#never mind this part 
'''
# Match test image to originals
def test_images(test_path,originals,names,threshold=0.88):
    #originals, names = load_original_embeddings(original_folder)
    test_emb = get_embedding(test_path)
    sims = cosine_similarity(test_emb, originals)[0]
    best_idx = np.argmax(sims)
    best_score = sims[best_idx]

    print(f"Best match: {names[best_idx]}")
    print(f"Similarity score: {best_score:.3f}")

    if best_score >= threshold:
        print(" Match found !")
    else:
        print(" No match found.")
#original_folder=r"C:\\Users\\LENOVO\\Documents\\PROJECTS\\pixel-peep\\images\\originals"
#originals, names = load_original_embeddings(original_folder)
#test_images(
    test_path=r"C:\\Users\\LENOVO\\Documents\\PROJECTS\\pixel-peep\\images\\test\\meme.png",
    originals=originals,
    names=names,
    threshold=0.88
#)'''