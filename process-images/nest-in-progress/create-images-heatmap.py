import cv2
import numpy as np
import os

# --- Configuration ---
INPUT_IMAGE = 'basetest-bird.jpg' 
BASELINE_IMAGE = 'baseline.jpg'
OUTPUT_DIR = 'analysis_steps_heatmap/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

DIFF_THRESHOLD = 35
MIN_BIRD_AREA = 2000

def save_step(name, img):
    path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    cv2.imwrite(path, img)
    print(f"Saved: {path}")

def visualize_with_heatmap():
    # 1. Load images
    img_color = cv2.imread(INPUT_IMAGE)
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    base_gray = cv2.imread(BASELINE_IMAGE, cv2.IMREAD_GRAYSCALE)
    
    if img_gray is None or base_gray is None:
        print("Error: Images not found.")
        return

    # STEP 1 & 2: Blurring and Delta
    img_blur = cv2.GaussianBlur(img_gray, (21, 21), 0)
    base_blur = cv2.GaussianBlur(base_gray, (21, 21), 0)
    frame_delta = cv2.absdiff(base_blur, img_blur)
    save_step("02_difference_map", frame_delta)

    # STEP 3: Thresholding
    _, thresh = cv2.threshold(frame_delta, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    save_step("03_binary_threshold", thresh)

    # STEP 4: Heatmap Generation
    # We apply a color map to the 'delta' (the raw difference)
    # This turns the grayscale difference into a "thermal" look
    heatmap_color = cv2.applyColorMap(frame_delta, cv2.COLORMAP_JET)
    
    # Optional: Overlay the heatmap onto the original image at 50% transparency
    overlay = cv2.addWeighted(img_color, 0.5, heatmap_color, 0.5, 0)
    save_step("04_heatmap_overlay", overlay)

    # STEP 5: Final Detection
    output_visual = img_color.copy()
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        if cv2.contourArea(c) > MIN_BIRD_AREA:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(output_visual, (x, y), (x + w, y + h), (0, 255, 0), 2)

    save_step("05_final_result", output_visual)
    print("\nVisual analysis complete!")

if __name__ == "__main__":
    visualize_with_heatmap()