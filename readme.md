# Birdbox Image Capture

Some scripts used to cpature images using a RPi, NOIR camera and IR LEDs.

Generates a web page with the latest image and some stats.

![screenshot](/web-screenshot.png)

### Crontab

```
# m h  dom mon dow   command
*/1 7-20 * * * sh /home/pi/camera.sh
# Run bird compare script at 11:27 PM everyday, then update the webpage by running camera.sh
27 23 * * * /usr/bin/python3 /home/pi/birdcompare-live.py ; /home/pi/camera.sh
```
