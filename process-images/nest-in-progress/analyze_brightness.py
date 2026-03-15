import cv2
import os
import numpy as np

BIRDS_DIR = 'birds/'
NO_BIRDS_DIR = 'no-birds/'

def analyze_brightness(directory):
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    brightness_values = []
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        img_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        
        if img_gray is not None:
            # Calculate the average brightness of the image (0 is black, 255 is white)
            avg_brightness = np.mean(img_gray)
            brightness_values.append((filename, avg_brightness))
            
    if not brightness_values:
         return 0, 0, 0, []
        
    values = [b for _, b in brightness_values]
    return np.mean(values), np.min(values), np.max(values), brightness_values

print("Analyzing brightness...")

bird_avg, bird_min, bird_max, bird_vals = analyze_brightness(BIRDS_DIR)
no_bird_avg, no_bird_min, no_bird_max, no_bird_vals = analyze_brightness(NO_BIRDS_DIR)

print(f"\n--- BIRDS ({len(bird_vals)} images) ---")
print(f"Average Brightness: {bird_avg:.2f}")
print(f"Min Brightness:     {bird_min:.2f}")
print(f"Max Brightness:     {bird_max:.2f}")

print(f"\n--- NO BIRDS ({len(no_bird_vals)} images) ---")
print(f"Average Brightness: {no_bird_avg:.2f}")
print(f"Min Brightness:     {no_bird_min:.2f}")
print(f"Max Brightness:     {no_bird_max:.2f}")

# Check overlap
bird_values = np.array([b for _, b in bird_vals])
no_bird_values = np.array([b for _, b in no_bird_vals])

overlap_threshold = (np.mean(bird_values) + np.mean(no_bird_values)) / 2
birds_below_thresh = np.sum(bird_values < overlap_threshold)
no_birds_above_thresh = np.sum(no_bird_values >= overlap_threshold)

print(f"\n--- THRESHOLD ANALYSIS ---")
print(f"Suggested Threshold: {overlap_threshold:.2f}")
print(f"Birds darker than threshold: {birds_below_thresh}/{len(bird_values)} ({(birds_below_thresh/len(bird_values)*100):.1f}%)")
print(f"No-Birds lighter than threshold: {no_birds_above_thresh}/{len(no_bird_values)} ({(no_birds_above_thresh/len(no_bird_values)*100):.1f}%)")

