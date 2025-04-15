import threading
import os
import sys
from pathlib import Path
import logging
# sys.path.append(str(Path(__file__).parent))
from src.monitor import start_monitoring, upload_trigger_loop, stop_monitoring
from src.config import LOCAL_SAVE_DIR, CONVERTED_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'snaplog.log')
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure required directories exist"""
    try:
        os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
        os.makedirs(CONVERTED_DIR, exist_ok=True)
        logger.info(f"Directories verified: {LOCAL_SAVE_DIR}, {CONVERTED_DIR}")
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        raise

def main():
    """Main application entry point"""
    try:
        ensure_directories()
        
        logger.info("Starting SnapLog monitoring service")
        
        monitor_thread = threading.Thread(
            target=start_monitoring,
            name="MonitorThread"
        )
        upload_thread = threading.Thread(
            target=upload_trigger_loop,
            name="UploadThread"
        )
        
        # Set threads as daemon so they'll exit when main thread exits
        monitor_thread.daemon = True
        upload_thread.daemon = True
        
        monitor_thread.start()
        upload_thread.start()
        logger.info("Service threads started")
        
        # Keep main thread alive
        while True:
            monitor_thread.join(timeout=1)
            upload_thread.join(timeout=1)
            
            if not monitor_thread.is_alive() or not upload_thread.is_alive():
                logger.warning("One of the service threads has stopped")
                break
                
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping...")
        stop_monitoring.set()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
    finally:
        stop_monitoring.set()
        logger.info("SnapLog service stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()