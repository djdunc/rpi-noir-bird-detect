#!/bin/bash

# first off turn on the IR LEDs'
#   Exports pin to userspace
sudo echo "4" > /sys/class/gpio/export  

# Sets pin 4 as an output
sudo echo "out" > /sys/class/gpio/gpio4/direction

# Sets pin 4 to high
sudo echo "1" > /sys/class/gpio/gpio4/value

# wait a couple of seconds for lights to settle
sleep 2

DATE=$(date +"%Y-%m-%d_%H%M")
libcamera-still --width 1920 --height 1080 -o /home/pi/timelapse/$DATE.jpg --tuning-file /usr/share/libcamera/ipa/rpi/vc4/ov5647_noir.json

# Sets pin 4 to low
sudo echo "0" > /sys/class/gpio/gpio4/value 

sudo cp "/home/pi/timelapse/$DATE.jpg" "/var/www/html/birdbox.jpg"

# create folder on rpi to hold timelapse images
# sudo chmod 777 camera.sh
# then add this to the crontab
# */1 * * * * sh /home/pi/camera.sh

# once per minute is about 2.1Gb a date - which is a lot on a 64GB card - 25 days

# Get disk space information
disk_space=$(df -h / | tail -n 1 | awk '{print $4}')
disk_space_perc=$(df / | tail -n 1 | awk '{print 100 - $5 "%"}')
filedate=$(date -d "$(stat -c "%y" /var/www/html/birdbox.jpg)")
file_count=$(ls /home/pi/today/ 2>/dev/null | wc -l)

# Copy the most recent bird image
latest_bird=$(ls -t /home/pi/today/*.jpg 2>/dev/null | head -1)
latest_bird_date="N/A"
if [ -n "$latest_bird" ]; then
    latest_bird_date=$(date -d "$(stat -c "%y" "$latest_bird")")
    sudo cp "$latest_bird" "/var/www/html/latest-bird.jpg"
fi

# Define the content you want to save as HTML
html_content="<html>
<head>
  <title>Birdbox</title>
</head>
<body>
  <h1>Birdbox - live view</h1>
  <img src=\"birdbox.jpg\" width=\"100%\">
  <p>Image updated: $filedate .</p>
  <p>Available Disk Space: $disk_space  (or $disk_space_perc)</p>
  <p>Images in today folder: $file_count</p>
  
  <h2>Last Bird Detected</h2>
  <img src=\"latest-bird.jpg\" width=\"100%\">
  <p>Image captured: $latest_bird_date</p>
</body>
</html>"

# Save the HTML content to a file
echo "$html_content" > index.html
sudo cp "/home/pi/index.html" "/var/www/html/index.html"
