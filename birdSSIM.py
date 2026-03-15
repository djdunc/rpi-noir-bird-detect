import cv2
import os
import shutil
from skimage.metrics import structural_similarity as ssim

# --- Configuration ---
BASELINE_PATH = 'baseline.jpg'  # Path to your known empty image
SOURCE_DIR = 'timelapse/'              # The folder containing all your images
BIRD_DIR = 'bird/'
EMPTY_DIR = 'empty/'
THRESHOLD = 0.85  # Higher (0.95) = more sensitive; Lower (0.70) = less sensitive

# Create destination folders if they don't exist
for folder in [BIRD_DIR, EMPTY_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def process_timelapse():
    # 1. Load and prep the baseline image
    baseline_img = cv2.imread(BASELINE_PATH, cv2.IMREAD_GRAYSCALE)
    if baseline_img is None:
        print(f"Error: Could not find baseline image at {BASELINE_PATH}")
        return
    
    # Smooth out sensor noise
    baseline_img = cv2.GaussianBlur(baseline_img, (5, 5), 0)
    h, w = baseline_img.shape

    # 2. Iterate through the timelapse folder
    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Found {len(files)} images to process...")

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        current_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        
        if current_img is None:
            continue

        # Ensure images are the same dimensions for comparison
        if current_img.shape != (h, w):
            current_img = cv2.resize(current_img, (w, h))

        # Prep current image
        current_img = cv2.GaussianBlur(current_img, (5, 5), 0)

        # 3. Calculate Similarity Score
        # score = 1.0 (Identical) | score < 1.0 (Different)
        score, _ = ssim(baseline_img, current_img, full=True)

        # 4. Sort based on the score
        if score < THRESHOLD:
            print(f"SORTED: {filename} -> BIRD (Score: {score:.2f})")
            shutil.move(file_path, os.path.join(BIRD_DIR, filename))
        else:
            print(f"SORTED: {filename} -> EMPTY (Score: {score:.2f})")
            shutil.move(file_path, os.path.join(EMPTY_DIR, filename))

    print("\nProcessing complete!")

if __name__ == "__main__":
    process_timelapse()
