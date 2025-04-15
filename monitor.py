# monitor.py

import os
import time
import mss
from datetime import datetime
from config import SCREENSHOT_INTERVAL, LOCAL_SAVE_DIR

os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

def take_screenshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(LOCAL_SAVE_DIR, f"screen_{timestamp}.binn")

    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  # capture screen
        with open(filename, "wb") as f:
            f.write(screenshot.rgb)  # save raw image bytes

    print(f"[+] Screenshot saved: {filename}")


def start_monitoring():
    while True:
        take_screenshot()
        time.sleep(SCREENSHOT_INTERVAL)

if __name__ == "__main__":
    start_monitoring()

