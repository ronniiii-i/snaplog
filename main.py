import os
import sys
from pathlib import Path
import logging
from src.monitor import run_service
from src.config import LOCAL_SAVE_DIR, NETWORK_BASE_PATH, CLIENT_CONFIG_FILE, DEVICE_ID, LOGS_DIR

# log_dir = os.path.join(os.path.dirname(__file__), 'logs')
log_dir = LOGS_DIR
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_dir, 'snaplog.log'),
    filemode='a'
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure required local and network directories exist."""
    try:
        # log blank new line for clarity in logs
        logger.info("\n\n" + "=" * 50 + "\n")
        logger.info("Ensuring required directories exist...")
    
        
        os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
        logger.info(f"Local directories verified: {LOCAL_SAVE_DIR}")

        os.makedirs(NETWORK_BASE_PATH, exist_ok=True)
        logger.info(f"Network base path verified: {NETWORK_BASE_PATH}")

        client_network_folder = os.path.join(NETWORK_BASE_PATH, DEVICE_ID)
        os.makedirs(client_network_folder, exist_ok=True)
        logger.info(f"Client's dedicated network folder verified: {client_network_folder}")

    except Exception as e:
        logger.critical(f"Failed to create directories: {e}", exc_info=True)
        raise

def main():
    """Main application entry point for the client."""
    try:
        ensure_directories()
        logger.info("Starting SnapLog client service.")
        run_service()
        
    except Exception as e:
        logger.critical(f"Fatal error in SnapLog client: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

