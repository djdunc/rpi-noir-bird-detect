import cv2
import os
import shutil
import numpy as np

# --- Configuration ---
BASELINE_PATH = 'baseline.jpg' 
SOURCE_DIR = 'timelapse/'
BIRD_DIR = 'today/'
NO_BIRDS_DIR = 'no-birds/'

# Create destination folders if they don't exist
os.makedirs(BIRD_DIR, exist_ok=True)
os.makedirs(NO_BIRDS_DIR, exist_ok=True)

# ADJUST THESE FOR TUNING:
DIFF_THRESHOLD = 35    # How much a pixel must change (0-255)
MIN_BIRD_AREA = 2000   # Min pixels for a bird (the bird in your photo is ~5000+)
LEARNING_RATE = 0.05   # How fast the background adapts to empty frames (e.g. 5%)
BIRD_BRIGHTNESS = 135  # Maximum average brightness of the detected object (0=black, 255=white)

def is_bird_detected(file_path, background_blur):
    img_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        return None, 0, None

    # 1. Blur the incoming frame
    working_gray = cv2.GaussianBlur(img_gray, (21, 21), 0)
    
    # 2. Calculate Difference against the passed background
    frame_delta = cv2.absdiff(background_blur, working_gray)
    
    # 3. Thresholding (creates a binary mask)
    thresh = cv2.threshold(frame_delta, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2) 

    # 4. Find Contours (Blobs)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    is_bird = False
    max_area = 0

    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            
        if area > MIN_BIRD_AREA:
            # 5. We found a big enough change. Let's see how dark this specific shape is.
            # Create a blank mask the same size as the image
            mask = np.zeros(img_gray.shape, dtype=np.uint8)
            # Draw the filled contour onto the mask
            cv2.drawContours(mask, [c], -1, 255, -1)
            # Calculate the average brightness of the original image, ONLY inside the mask
            mean_val = cv2.mean(img_gray, mask=mask)[0]

            if mean_val < BIRD_BRIGHTNESS:
                is_bird = True
                # We stop at the first dark blob found
                break

    return is_bird, max_area, working_gray

def process_timelapse():

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    # IMPORTANT: Ensure chronological order so the background grows organically
    files.sort()
    
    if not files:
        print(f"No files found in {SOURCE_DIR}")
        return

    print(f"Processing {len(files)} files in {SOURCE_DIR} chronologically...")

    # Initialize dynamic background average with the FIRST frame of the timelapse!
    # This prevents the entire sequence from starting out "stuck" if the nest has 
    # already evolved significantly since baseline.jpg was taken.
    first_frame_path = os.path.join(SOURCE_DIR, files[0])
    first_img = cv2.imread(first_frame_path, cv2.IMREAD_GRAYSCALE)
    first_blur = cv2.GaussianBlur(first_img, (21, 21), 0)
    avg_background = np.float32(first_blur)

    frames_processed = 0

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)

        # Get current background estimate as 8-bit integer
        current_bg = cv2.convertScaleAbs(avg_background)

        is_bird, max_area, working_gray = is_bird_detected(file_path, current_bg)
        
        if is_bird is None:
            continue

        frames_processed += 1

        if is_bird:
            print(f"BIRD DETECTED: {filename} (Area: {int(max_area)})")
            # We completely PAUSE learning the background when a bird is present.
            # This prevents the bird from being "absorbed" into the background and causing False Negatives
            shutil.move(file_path, os.path.join(BIRD_DIR, filename))
        else:
            print(f"EMPTY: {filename} (Max Area: {int(max_area)})")
            # Update the background model more quickly when no bird is detected (e.g. 5%)
            cv2.accumulateWeighted(working_gray, avg_background, LEARNING_RATE)
            shutil.move(file_path, os.path.join(NO_BIRDS_DIR, filename))
                
if __name__ == "__main__":
    process_timelapse()