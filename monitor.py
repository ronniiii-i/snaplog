import os
import time
import mss
import threading
import subprocess
from datetime import datetime
from config import SCREENSHOT_INTERVAL, LOCAL_SAVE_DIR, DAILY_UPLOAD_TIME

stop_monitoring = threading.Event()
os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

def take_screenshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(LOCAL_SAVE_DIR, f"screen_{timestamp}.binn")

    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        with open(filename, "wb") as f:
            f.write(screenshot.rgb)

    print(f"[+] Screenshot saved: {filename}")


def start_monitoring():
    while not stop_monitoring.is_set():
        take_screenshot()
        stop_monitoring.wait(timeout=SCREENSHOT_INTERVAL)
        

def upload_trigger_loop():
    last_checked = None
    while True:
        now = datetime.now().strftime("%H:%M")
        print(f"[+] Current time: {now}")
        if now == DAILY_UPLOAD_TIME and now != last_checked:
            print("[*] Running convert.py for transfer...")
            stop_monitoring.set()
            subprocess.run(["python", "convert.py"])
            last_checked = now
            time.sleep(60)
            os._exit(0)
        time.sleep(1)



if __name__ == "__main__":
    monitor_thread = threading.Thread(target=start_monitoring)
    upload_thread = threading.Thread(target=upload_trigger_loop)

    monitor_thread.start()
    upload_thread.start()

    monitor_thread.join()
    upload_thread.join()

    print("[+] All tasks complete. Exiting.")
