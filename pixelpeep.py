import os
import gc
import time
import pickle
import imagehash
from PIL import Image
from itertools import islice
from multiprocessing import Process, Event, Queue

image_hashes = {}
hash_chunks = []

# load the trained image hashes from the saved file
def load_trained_img_hashes():
    global image_hashes
    global hash_chunks
    if len(hash_chunks) == 0 and os.path.exists('trained_img_hashes.pkl'):
        print("Loading trained image hashes...")
        with open('trained_img_hashes.pkl', 'rb') as file:
            image_hashes = pickle.load(file)
    
        process_count = 2 
        total_hashes = len(image_hashes)
        split_size = total_hashes // process_count if total_hashes > process_count * process_count else process_count
        hash_chunks = list(split_dict(image_hashes, split_size))
        del image_hashes
        gc.collect()

# get the dict item by index
def get_dict_item_by_index(dict, start):
    return next(islice(dict.items(), start, None))

# split the dict into chunks
def split_dict(d, chunk_size):
    it = iter(d.items())
    for _ in range(0, len(d), chunk_size):
        yield dict(islice(it, chunk_size))

# generate hash of the image
def getHash(image):
    image = image.convert("L").resize((32, 32))
    return imagehash.dhash(image)

# save the trained image hashes to a file
def saveImageHashes():
    global image_hashes
    with open('trained_img_hashes.pkl', 'wb') as file:
        pickle.dump(image_hashes, file)

# check if the image is valid
def is_valid_image(image_path):
    if not os.path.isfile(image_path):
        return False
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        return False
    return True

# generate hash for the variants of source image 
def hash_source_variants(image_path, filename):
    global image_hashes
    image = Image.open(image_path)

    #rotated case
    for angle in range(0, 360, 90):
        rotated_image = image.rotate(angle)
        image_hash = getHash(rotated_image)
        if angle == 0 and image_hash in image_hashes:
            return False
        image_hashes[image_hash] = filename

    # flipped case
    for flip in [Image.FLIP_LEFT_RIGHT, Image.FLIP_TOP_BOTTOM]:
        flipped_image = image.transpose(flip)
        image_hash = getHash(flipped_image)
        image_hashes[image_hash] = filename

    return True

# algorithm to find the minimum difference between 2 image hashes
def get_min_image_hash(image_hash, image_hashes, event, result_queue):
    min = float('inf')
    file_name = None
    max_difference_score = 3.2 # 3.2 => 95%, 6.4 => 90%, 12.8 => 80% --similarity

    left = 0
    right = len(image_hashes) - 1
    while left <= right:

        if event.is_set():
            break

        hash = get_dict_item_by_index(image_hashes, left)
        diff = image_hash - hash[0]
        if diff < max_difference_score and diff < min:
            min = diff
            file_name = hash[1]

        hash = get_dict_item_by_index(image_hashes, right)
        diff = image_hash - hash[0]
        if diff < max_difference_score and diff < min:
            min = diff
            file_name = hash[1]

        if min == 0:
            event.set()
            break
        
        left += 1
        right -= 1
    
    result_queue.put([min, file_name])
    

# train the images and generate hashes
def train_images(image_folder):
    global image_hashes
    trained_img_count = 0
    total_img_count = 0
    if not os.path.exists(image_folder) or not os.path.isdir(image_folder):
        print(f"Error: Invalid path - {image_folder}")
        return
    
    start_time = time.time()
    for filename in os.listdir(image_folder):
        image_path = os.path.abspath(os.path.join(image_folder, filename))

        if not is_valid_image(image_path):
            print(f"Skipping {filename} :: Error opening image")
            continue

        total_img_count += 1

        if not hash_source_variants(image_path, filename):
            print(f"Skipping {filename} :: Image already exist")
            continue

        trained_img_count += 1

    elapsed_time = time.time() - start_time
    saveImageHashes()

    print(f"Training completed in {elapsed_time:.4f} seconds.")
    print(f"Trained {trained_img_count} out of {total_img_count} images.")
    print(f"Total hashes: {len(image_hashes)}")


# test the images and find similar images
def test_images(image_path):
    global image_hashes
    global hash_chunks

    image_path = os.path.abspath(image_path)
    
    if not is_valid_image(image_path):
        print(f"Skipping {image_path} :: Error opening image")
        return
    
    load_trained_img_hashes()

    start_time = time.time()
    test_image_hash = getHash(Image.open(image_path))

    event = Event()
    result_queue = Queue()

    processes = []
    for hash_chunk in hash_chunks:
        process = Process(target=get_min_image_hash, args=(test_image_hash, hash_chunk, event, result_queue))
        processes.append(process)
        process.start()
    
    results = []
    for process in processes:
        results.append(result_queue.get())
        process.join()
        
    min_hash = min(results, key=lambda x: x[0])
    min_hash_value = min_hash[0]
    min_hash_filename = min_hash[1]

    if min_hash_filename:
        print(f"Similar Image found: {min_hash_filename} with {100 - (min_hash_value / 64) * 100:.2f}% similarity. [{(time.time() - start_time):.4f} seconds]")
    else:
        print(f"No similar image found. [{(time.time() - start_time):.4f} seconds]")


train_images("downloaded_images")
test_images("variants/test_1.jpg")
test_images("variants/test_2.jpg")
test_images("variants/test_3.jpg")
