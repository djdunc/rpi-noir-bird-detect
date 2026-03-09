import cv2
import os
import shutil
import numpy as np

# --- Configuration ---
BASELINE_PATH = 'baseline.jpg' 
SOURCE_DIR = 'timelapse/'
BIRDS_EVAL_DIR = 'birds/'
NO_BIRDS_EVAL_DIR = 'no-birds/'

# Output folders
BIRD_DIR = 'today/'

# ADJUST THESE FOR TUNING:
DIFF_THRESHOLD = 50    # How much a pixel must change (0-255)
MIN_BIRD_AREA = 1600   # Min pixels for a bird (the bird in your photo is ~5000+)

# Create destination folder
os.makedirs(BIRD_DIR, exist_ok=True)

def is_bird_detected(file_path, baseline_blur):
    img_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        return None, 0

    # 1. Calculate Difference
    working_gray = cv2.GaussianBlur(img_gray, (21, 21), 0)
    frame_delta = cv2.absdiff(baseline_blur, working_gray)
    
    # 2. Thresholding (creates a binary mask)
    thresh = cv2.threshold(frame_delta, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2) 

    # 3. Find Contours (Blobs)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    is_bird = False
    max_area = 0

    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
        
        if area > MIN_BIRD_AREA:
            is_bird = True
            # We stop at the first big blob found
            break

    return is_bird, max_area

def evaluate_accuracy(baseline_blur):
    print("--- Evaluating Accuracy on Known Examples ---")
    
    tp = 0
    fn = 0
    if os.path.exists(BIRDS_EVAL_DIR):
        bird_files = [f for f in os.listdir(BIRDS_EVAL_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for f in bird_files:
            detected, _ = is_bird_detected(os.path.join(BIRDS_EVAL_DIR, f), baseline_blur)
            if detected:
                tp += 1
            else:
                fn += 1
                
    tn = 0
    fp = 0
    if os.path.exists(NO_BIRDS_EVAL_DIR):
        empty_files = [f for f in os.listdir(NO_BIRDS_EVAL_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for f in empty_files:
            detected, _ = is_bird_detected(os.path.join(NO_BIRDS_EVAL_DIR, f), baseline_blur)
            if not detected:
                tn += 1
            else:
                fp += 1
                
    total_eval = tp + fn + tn + fp
    if total_eval > 0:
        accuracy = (tp + tn) / total_eval * 100
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Correctly identified birds (True Positives): {tp}/{tp+fn}")
        print(f"Correctly identified empty (True Negatives): {tn}/{tn+fp}")
        if fn > 0: print(f"Missed Birds (False Negatives): {fn}")
        if fp > 0: print(f"False Alarms (False Positives): {fp}")
    else:
        print("No evaluation images found.")
    print("---------------------------------------------\n")

def process_timelapse():
    # Load and prep baseline
    baseline_img = cv2.imread(BASELINE_PATH, cv2.IMREAD_GRAYSCALE)
    if baseline_img is None:
        print(f"Error: {BASELINE_PATH} not found.")
        return
    
    # High blur helps ignore sensor grain/noise in the dark
    baseline_blur = cv2.GaussianBlur(baseline_img, (21, 21), 0)

    # First evaluate parameters
    evaluate_accuracy(baseline_blur)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Processing {len(files)} files in {SOURCE_DIR}...")

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)

        is_bird, max_area = is_bird_detected(file_path, baseline_blur)
        
        if is_bird is None:
            continue

        if is_bird:
            print(f"BIRD DETECTED: {filename} (Area: {int(max_area)})")
            shutil.move(file_path, os.path.join(BIRD_DIR, filename))
        else:
            print(f"EMPTY: {filename} (Max Area: {int(max_area)})")
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error removing {file_path}: {e}")

if __name__ == "__main__":
    process_timelapse()