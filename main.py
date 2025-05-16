import os
import sys
from pathlib import Path
import logging
from src.monitor import run_service
from src.config import LOCAL_SAVE_DIR
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_dir, 'snaplog.log'),
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure required directories exist"""
    try:
        os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
        # os.makedirs(CONVERTED_DIR, exist_ok=True)
        logger.info(f"Directories verified: {LOCAL_SAVE_DIR}")
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        raise

def main():
    """Main application entry point"""
    try:
        ensure_directories()
        logger.info("Starting SnapLog service")
        run_service()  # This will run until interrupted
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()