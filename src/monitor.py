import os
import time
import mss
import threading
from datetime import datetime
from src.config import SCREENSHOT_INTERVAL, LOCAL_SAVE_DIR, DAILY_UPLOAD_TIME
from src.operations import SnapLogOperations

class MonitorService:
    def __init__(self):
        self.stop_monitoring = threading.Event()
        os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
        self.ops = SnapLogOperations()  # Initialize once

    def take_screenshot(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(LOCAL_SAVE_DIR, f"screen_{timestamp}.binn")

        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            with open(filename, "wb") as f:
                f.write(screenshot.rgb)
        print(f"[+] Screenshot saved: {filename}")

    def start_monitoring(self):
        while not self.stop_monitoring.is_set():
            self.take_screenshot()
            self.stop_monitoring.wait(timeout=SCREENSHOT_INTERVAL)

    def upload_trigger_loop(self):
        last_checked = None
        while True:
            now = datetime.now().strftime("%H:%M")
            if now == DAILY_UPLOAD_TIME and now != last_checked:
                print("\n" + "="*50)
                print("[*] Running conversion and transfer...")
                self.stop_monitoring.set()  # Stop monitoring

                try:
                    # NEW: Verify files exist before conversion
                    binn_files = [f for f in os.listdir(LOCAL_SAVE_DIR) if f.endswith(".binn")]
                    print(f"Found {len(binn_files)} screenshots to process")

                    if self.ops.run_conversion_and_transfer():
                        print("[✓] Transfer completed successfully")
                    else:
                        print("[!] Transfer failed - see logs for details")

                except Exception as e:
                    print(f"[!!!] CRITICAL ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # NEW: Ensure monitoring restarts even after failure

                finally:
                    last_checked = now
                    time.sleep(60)
                    print("[*] Monitoring stopped after transfer.")
                    os._exit(0)

            time.sleep(1)
def run_service():
    service = MonitorService()
    monitor_thread = threading.Thread(
        target=service.start_monitoring,
        name="MonitorThread",
        daemon=True
    )
    upload_thread = threading.Thread(
        target=service.upload_trigger_loop,
        name="UploadThread",
        daemon=True
    )
    
    monitor_thread.start()
    upload_thread.start()
    
    try:
        while True:
            if not upload_thread.is_alive():
                print("[✓] Upload thread finished.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[+] Shutting down...")
        service.stop_monitoring.set()
