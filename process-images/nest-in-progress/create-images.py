import cv2
import numpy as np
import os

# --- Setup ---
# Replace these with your actual filenames for testing
INPUT_IMAGE = 'basetest-bird.jpg' 
BASELINE_IMAGE = 'baseline.jpg'
OUTPUT_DIR = 'analysis_steps/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Settings from your original script
DIFF_THRESHOLD = 35
MIN_BIRD_AREA = 2000

def save_step(name, img):
    path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    cv2.imwrite(path, img)
    print(f"Saved: {path}")

def visualize_analysis():
    # 1. Load images in Grayscale
    img = cv2.imread(INPUT_IMAGE, cv2.IMREAD_GRAYSCALE)
    base = cv2.imread(BASELINE_IMAGE, cv2.IMREAD_GRAYSCALE)
    
    if img is None or base is None:
        print("Error: Could not find input or baseline image.")
        return

    # STEP 1: Blurring (Noise Reduction)
    # We blur to stop the computer from over-reacting to tiny pixel grain.
    img_blur = cv2.GaussianBlur(img, (21, 21), 0)
    base_blur = cv2.GaussianBlur(base, (21, 21), 0)
    save_step("01_blurred_input", img_blur)

    # STEP 2: The Delta (Difference)
    # This subtracts the baseline from the current frame. 
    # Only things that MOVED or CHANGED will be bright.
    frame_delta = cv2.absdiff(base_blur, img_blur)
    save_step("02_difference_map", frame_delta)

    # STEP 3: Thresholding
    # We turn the delta into pure Black and White.
    # Anything above DIFF_THRESHOLD becomes white (255).
    _, thresh = cv2.threshold(frame_delta, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
    # Dilate makes the white spots "thicker" to close gaps in the bird's shape
    thresh = cv2.dilate(thresh, None, iterations=2) 
    save_step("03_binary_threshold", thresh)

    # STEP 4: Final Detection (Contours)
    # We draw a green box around anything larger than MIN_BIRD_AREA.
    output_visual = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv2.contourArea(c)
        if area > MIN_BIRD_AREA:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(output_visual, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(output_visual, f"Area: {int(area)}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    save_step("04_final_detection", output_visual)
    print("\nAnalysis Complete! Check the 'analysis_steps' folder.")

if __name__ == "__main__":
    visualize_analysis()