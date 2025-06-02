import os
import time
import mss
import threading
from datetime import datetime, timedelta
import logging

# Import updated config module
from src.config import LOCAL_SAVE_DIR, load_client_config, DEVICE_ID
from src.operations import SnapLogOperations

logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(self):
        self.stop_monitoring = threading.Event()
        os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
        self.ops = SnapLogOperations() # Initialize operations
        self.current_config = load_client_config() # Load initial config
        self.last_upload_time = None # To track last periodic upload
        logger.info(f"MonitorService initialized for device: {DEVICE_ID}")
        logger.info(f"Initial configuration: {self.current_config}")

    def take_screenshot(self):
        """Captures a screenshot and saves it as a .binn file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(LOCAL_SAVE_DIR, f"screen_{timestamp}.binn")

        try:
            with mss.mss() as sct:
                # Assuming monitor 1 is the primary, adjust if needed
                # sct.monitors[0] is the entire screen, sct.monitors[1] is the first monitor.
                # If you have multiple monitors, you might need to adjust this or iterate.
                monitor = sct.monitors[1] # Or sct.monitors[0] for primary display
                screenshot = sct.grab(monitor)
                with open(filename, "wb") as f:
                    f.write(screenshot.rgb)
            logger.info(f"[+] Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            # If screenshot fails, still allow the loop to continue
            pass

    def start_monitoring(self):
        """Continuously takes screenshots at the configured interval."""
        while not self.stop_monitoring.is_set():
            self.take_screenshot()
            # Wait for the configured interval, checking for stop signal
            self.stop_monitoring.wait(timeout=self.current_config["screenshot_interval"])
            # Periodically reload config to pick up changes
            self.current_config = load_client_config()
            logger.debug(f"Monitoring with interval: {self.current_config['screenshot_interval']}s")

    def upload_trigger_loop(self):
        """Manages the upload schedule based on dynamic configuration."""
        last_checked_daily_time = None # To prevent multiple daily uploads within the same minute

        while True:
            # Always reload config to get the latest settings for upload
            self.current_config = load_client_config()
            upload_type = self.current_config["upload_type"]
            upload_value = self.current_config["upload_value"]
            
            now = datetime.now()
            
            should_upload = False

            if upload_type == "daily":
                target_time_str = str(upload_value) # Ensure it's a string like "HH:MM"
                current_time_str = now.strftime("%H:%M")
                
                if current_time_str == target_time_str and current_time_str != last_checked_daily_time:
                    should_upload = True
                    last_checked_daily_time = current_time_str # Mark as checked for this minute
                elif current_time_str != last_checked_daily_time:
                    # Reset last_checked_daily_time if the minute changes, so it can trigger again next day
                    last_checked_daily_time = None 

            elif upload_type == "periodic":
                try:
                    interval_seconds = int(upload_value)
                    if self.last_upload_time is None:
                        # First run, or after service restart, upload immediately
                        should_upload = True
                        self.last_upload_time = now
                    elif (now - self.last_upload_time).total_seconds() >= interval_seconds:
                        should_upload = True
                        self.last_upload_time = now
                except ValueError:
                    logger.error(f"Invalid periodic upload value: {upload_value}. Expected seconds (integer).")
                    # Fallback to a default periodic check if value is invalid
                    time.sleep(60)
                    continue
            else:
                logger.warning(f"Unknown upload type: {upload_type}. Skipping upload check.")

            if should_upload:
                logger.info("\n" + "="*50)
                logger.info(f"[*] Upload triggered for {upload_type} schedule.")
                
                # Signal monitoring thread to pause (optional, if you want to ensure no new screenshots during upload)
                # self.stop_monitoring.set() 
                
                try:
                    binn_files = [f for f in os.listdir(LOCAL_SAVE_DIR) if f.endswith(".binn")]
                    logger.info(f"Found {len(binn_files)} screenshots to transfer.")

                    if self.ops.run_transfer_pipeline():
                        logger.info("[✓] Transfer completed successfully.")
                    else:
                        logger.warning("[!] Transfer failed or no files were transferred - see logs for details.")

                except Exception as e:
                    logger.critical(f"[!!!] CRITICAL ERROR during upload process: {str(e)}")
                    import traceback
                    traceback.print_exc()
                finally:
                    # After upload (success or failure), ensure monitoring can resume
                    # self.stop_monitoring.clear() 
                    logger.info("[*] Upload process finished. Monitoring continues.")
            
            time.sleep(1) # Check every second

def run_service():
    """Starts the client monitoring and upload services."""
    service = MonitorService()
    
    monitor_thread = threading.Thread(
        target=service.start_monitoring,
        name="MonitorThread",
        daemon=True # Daemon threads exit when the main program exits
    )
    upload_thread = threading.Thread(
        target=service.upload_trigger_loop,
        name="UploadThread",
        daemon=True # Daemon threads exit when the main program exits
    )
    
    monitor_thread.start()
    upload_thread.start()
    
    logger.info("SnapLog client service started. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive so daemon threads can run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[+] Shutting down SnapLog client service...")
        service.stop_monitoring.set() # Signal monitoring thread to stop
        # Give threads a moment to clean up if they need to
        monitor_thread.join(timeout=5)
        upload_thread.join(timeout=5)
        logger.info("SnapLog client service stopped.")
