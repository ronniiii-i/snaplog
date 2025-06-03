# main.py (Client)
import os
import sys
from pathlib import Path
import logging
from src.monitor import run_service
from src.config import LOCAL_SAVE_DIR, NETWORK_BASE_PATH, CLIENT_CONFIG_FILE, LOGS_DIR

# Configure logging to a file in the 'logs' directory
# log_dir = os.path.join(os.path.dirname(__file__), 'logs')
log_dir = LOGS_DIR
os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists

logging.basicConfig(
    level=logging.INFO, # Set to INFO for general operation, DEBUG for more verbosity
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_dir, 'snaplog.log'),
    filemode='a' # Append to log file
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure required local and network directories exist."""
    try:
        os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
        # os.makedirs(CONVERTED_DIR, exist_ok=True) # This might not be strictly needed on client anymore
        os.makedirs(NETWORK_BASE_PATH, exist_ok=True) # Ensure base network path exists for config file
        logger.info(f"Local directories verified: {LOCAL_SAVE_DIR}")
        logger.info(f"Network base path verified: {NETWORK_BASE_PATH}")
    except Exception as e:
        logger.critical(f"Failed to create directories: {e}", exc_info=True)
        raise

def main():
    """Main application entry point for the client."""
    try:
        ensure_directories()
        logger.info("Starting SnapLog client service.")
        run_service() # This will run until interrupted by Ctrl+C
        
    except Exception as e:
        logger.critical(f"Fatal error in SnapLog client: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()