#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys

def create_timelapse(input_folder, output_file, framerate):
    # Verify input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Directory '{input_folder}' does not exist.")
        sys.exit(1)
        
    # Check if there are actually jpg/png files in the folder
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        print(f"Error: No image files (.jpg, .jpeg, .png) found in '{input_folder}'.")
        sys.exit(1)
        
    print(f"Found {len(files)} images in '{input_folder}'.")
    print(f"Generating timelapse at {framerate} frames per second...")
    
    # We use ffmpeg with the glob pattern type to ensure chronological ordering regardless of 
    # file naming format, as long as they sort alphabetically.
    input_pattern = os.path.join(input_folder, '*.jpg')
    
    command = [
        "ffmpeg",
        "-y",               # Overwrite output file if it exists
        "-framerate", str(framerate),
        "-pattern_type", "glob",
        "-i", input_pattern,
        "-c:v", "libx264",  # widely compatible codec
        "-pix_fmt", "yuv420p", # ensures playback on all players like QuickTime
        output_file
    ]
    
    try:
        # Run ffmpeg
        subprocess.run(command, check=True)
        print(f"\nSuccess! Timelapse saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"\nError: ffmpeg failed to create the timelapse.")
        print("Please ensure 'ffmpeg' is installed and accessible.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\nError: 'ffmpeg' command not found on your system.")
        print("You can install it via Homebrew: brew install ffmpeg")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a timelapse MP4 from a folder of images.")
    parser.add_argument("-i", "--input", default="nest-images", help="Input directory containing images (default: 'nest-images')")
    parser.add_argument("-o", "--output", default="timelapse.mp4", help="Output video file name (default: 'timelapse.mp4')")
    parser.add_argument("-fps", "--framerate", type=int, default=10, help="Frames per second in the output video (default: 10)")
    
    args = parser.parse_args()
    
    create_timelapse(args.input, args.output, args.framerate)
