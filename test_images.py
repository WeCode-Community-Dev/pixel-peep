from sklearn.metrics.pairwise import cosine_similarity
from train import originals, names, get_embedding
import numpy as np

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

test_images(
    test_path=r"C:\\Users\\LENOVO\\Documents\\PROJECTS\\pixel-peep\\images\\test\\meme.png",
    originals=originals,
    names=names,
    threshold=0.80
)