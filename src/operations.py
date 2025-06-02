import os
import wmi
import subprocess
from datetime import datetime
import logging
import traceback
import shutil

# Import the updated config, specifically DEVICE_ID and NETWORK_BASE_PATH
from src.config import LOCAL_SAVE_DIR, DEVICE_ID, NETWORK_BASE_PATH

logger = logging.getLogger(__name__)

class SnapLogOperations:
    def __init__(self):
        self.device_id = DEVICE_ID # Use the DEVICE_ID from config
        # Construct the specific network path for this device's raw screenshots
        self.network_device_raw_path = os.path.join(NETWORK_BASE_PATH, self.device_id, "raw")
        logger.info(f"Client network upload path: {self.network_device_raw_path}")

    def _ensure_network_dir(self):
        """Ensure the device-specific network directory for raw files exists."""
        try:
            if not os.path.exists(self.network_device_raw_path):
                os.makedirs(self.network_device_raw_path, exist_ok=True)
                logger.info(f"[NETWORK] Created network directory: {self.network_device_raw_path}")
            else:
                logger.info(f"[NETWORK] Network directory exists: {self.network_device_raw_path}")
            return True
        except Exception as e:
            logger.error(f"[NETWORK] Failed to access or create directory {self.network_device_raw_path}: {str(e)}")
            traceback.print_exc()
            return False

    def transfer_files(self):
        """Transfer files from LOCAL_SAVE_DIR to the device-specific network raw path."""
        if not self._ensure_network_dir():
            logger.warning("Network directory not accessible, skipping file transfer.")
            return False

        files_to_transfer = [f for f in os.listdir(LOCAL_SAVE_DIR) if f.endswith(".binn")]
        if not files_to_transfer:
            logger.info("[!] No .binn files to transfer in local save directory.")
            return False

        success_count = 0
        for file in files_to_transfer:
            local_path = os.path.join(LOCAL_SAVE_DIR, file)
            network_path = os.path.join(self.network_device_raw_path, file)

            try:
                logger.info(f"[→] Transferring {file} to {self.network_device_raw_path}...")
                shutil.copy2(local_path, network_path)

                # Verify transfer by size
                if os.path.exists(network_path) and os.path.getsize(local_path) == os.path.getsize(network_path):
                    os.remove(local_path) # Remove local file after successful transfer
                    success_count += 1
                    logger.info(f"[✓] Successfully transferred and removed local file: {file}")
                else:
                    logger.warning(f"[!] Size mismatch or file not found on network for {file}. Keeping local copy.")

            except Exception as e:
                logger.error(f"[!] Failed to transfer {file}: {str(e)}")
                traceback.print_exc()
                continue

        logger.info(f"Transferred {success_count} out of {len(files_to_transfer)} files.")
        return success_count > 0

    def run_transfer_pipeline(self):
        """Orchestrate the file transfer workflow."""
        try:
            transfer_result = self.transfer_files()
            if not transfer_result:
                logger.warning("[!] File transfer pipeline completed with no successful transfers or encountered issues.")
                return False
            logger.info("[✓] File transfer pipeline completed successfully.")
            return True
        except Exception as e:
            logger.critical(f"[!!!] Fatal error in transfer pipeline: {str(e)}")
            traceback.print_exc()
            return False

