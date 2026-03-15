import cv2
import os
import numpy as np

BIRDS_DIR = 'birds/'
NO_BIRDS_DIR = 'no-birds/'
BASELINE_PATH = 'baseline.jpg'

def evaluate_method(method_name, detection_func, files_bird, files_empty):
    tp, fn, tn, fp = 0, 0, 0, 0
    
    for f in files_bird:
        if detection_func(f):
            tp += 1
        else:
            fn += 1
            
    for f in files_empty:
        if not detection_func(f):
            tn += 1
        else:
            fp += 1
            
    total = tp + fn + tn + fp
    accuracy = (tp + tn) / total * 100 if total > 0 else 0
    
    print(f"\n--- {method_name} ---")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"True Positives (Birds correctly found): {tp}/{len(files_bird)}")
    print(f"True Negatives (Empty correctly found): {tn}/{len(files_empty)}")
    print(f"False Negatives (Missed birds): {fn}")
    print(f"False Positives (False alarms): {fp}")


def main():
    bird_files = [os.path.join(BIRDS_DIR, f) for f in os.listdir(BIRDS_DIR) if f.lower().endswith('.jpg')]
    empty_files = [os.path.join(NO_BIRDS_DIR, f) for f in os.listdir(NO_BIRDS_DIR) if f.lower().endswith('.jpg')]

    baseline_img = cv2.imread(BASELINE_PATH, cv2.IMREAD_GRAYSCALE)
    if baseline_img is None:
         print("Missing baseline.jpg")
         return
    baseline_blur = cv2.GaussianBlur(baseline_img, (21, 21), 0)

    # METHOD 1: Simple Brightness Threshold (158)
    def method_brightness(file_path):
        img_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        return np.mean(img_gray) < 158.5

    # METHOD 2: AbsDiff (Our previous static baseline logic)
    def method_absdiff(file_path, threshold, min_area):
        img_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        working_gray = cv2.GaussianBlur(img_gray, (21, 21), 0)
        frame_delta = cv2.absdiff(baseline_blur, working_gray)
        thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2) 
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) > min_area: return True
        return False

    def method_absdiff_50(f): return method_absdiff(f, 50, 1600)
    def method_absdiff_30(f): return method_absdiff(f, 30, 1600)

    # METHOD 3: Subtract (Only changes that are DARKER than the baseline)
    def method_subtract(file_path, threshold, min_area):
        img_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        working_gray = cv2.GaussianBlur(img_gray, (21, 21), 0)
        # Background - Frame = Positive numbers only where frame is darker than background
        frame_delta = cv2.subtract(baseline_blur, working_gray)
        thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2) 
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) > min_area: return True
        return False
        
    def method_subtract_30(f): return method_subtract(f, 30, 1600)

    # METHOD 5: Static Subtract Darker Only (Lower Thresh=20, Larger Area=2000)
    def method_subtract_20_2000(file_path):
        return method_subtract(file_path, 20, 2000)

    # METHOD 6: Combined method (Subtract + Global Brightness)
    def method_combined(file_path):
        # Must be generally dark enough AND have a big enough dark change
        return method_brightness(file_path) and method_subtract(file_path, 30, 1600)

    evaluate_method("METHOD 1: Simple Brightness (Mean < 158.5)", method_brightness, bird_files, empty_files)
    evaluate_method("METHOD 2: Static AbsDiff (Thresh=50, Area=1600)", method_absdiff_50, bird_files, empty_files)
    evaluate_method("METHOD 3: Static AbsDiff (Lower Thresh=30, Area=1600)", method_absdiff_30, bird_files, empty_files)
    evaluate_method("METHOD 4: Static Subtract Darker Only (Thresh=30, Area=1600)", method_subtract_30, bird_files, empty_files)
    evaluate_method("METHOD 5: Static Subtract Darker Only (Lower Thresh=20, Larger Area=2000)", method_subtract_20_2000, bird_files, empty_files)
    evaluate_method("METHOD 6: Combined (Brightness < 158.5 AND Subtract(30,1600))", method_combined, bird_files, empty_files)


if __name__ == "__main__":
    main()
