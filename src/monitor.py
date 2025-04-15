import os
import time
import mss
import threading
import subprocess
from datetime import datetime
from src.config import SCREENSHOT_INTERVAL, LOCAL_SAVE_DIR, DAILY_UPLOAD_TIME
from src.operations import SnapLogOperations

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
        if now == DAILY_UPLOAD_TIME and now != last_checked:
            print("[*] Running conversion and transfer...")
            stop_monitoring.set()  # Stop monitoring
            
            try:
                ops = SnapLogOperations()
                if ops.run_conversion_and_transfer():
                    print("[✓] Transfer completed successfully")
                else:
                    print("[!] Transfer failed or no files to transfer")
            except Exception as e:
                print(f"[!] Critical error during transfer: {str(e)}")
            
            last_checked = now
            time.sleep(60)  # Prevent immediate retrigger
            stop_monitoring.clear()  # Reset the flag
            print("[*] Resuming monitoring...")
            start_monitoring()  # Restart monitoring
            
        time.sleep(1)



if __name__ == "__main__":
    monitor_thread = threading.Thread(target=start_monitoring)
    upload_thread = threading.Thread(target=upload_trigger_loop)

    monitor_thread.start()
    upload_thread.start()

    monitor_thread.join()
    upload_thread.join()

    print("[+] All tasks complete. Exiting.")
