import os
import wmi
import subprocess
from datetime import datetime
import logging
import traceback
import shutil
import json # New import for JSON handling

# Import the updated config, specifically DEVICE_ID and NETWORK_BASE_PATH
from src.config import LOCAL_SAVE_DIR, DEVICE_ID, NETWORK_BASE_PATH

logger = logging.getLogger(__name__)

class SnapLogOperations:
    def __init__(self):
        self.device_id = DEVICE_ID # Use the DEVICE_ID from config
        # Construct the specific network path for this device's raw screenshots
        self.network_device_raw_path = os.path.join(NETWORK_BASE_PATH, self.device_id)
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
        """Transfer files from LOCAL_SAVE_DIR to the device-specific network raw path.
           Transfers both .binn and corresponding .json metadata files."""
        if not self._ensure_network_dir():
            logger.warning("Network directory not accessible, skipping file transfer.")
            return False

        # Get all .binn files, then find their corresponding .json files
        binn_files_to_transfer = [f for f in os.listdir(LOCAL_SAVE_DIR) if f.endswith(".binn")]
        
        if not binn_files_to_transfer:
            logger.info("[!] No .binn files to transfer in local save directory.")
            return False

        success_count = 0
        for binn_file in binn_files_to_transfer:
            local_binn_path = os.path.join(LOCAL_SAVE_DIR, binn_file)
            network_binn_path = os.path.join(self.network_device_raw_path, binn_file)
            
            # Find corresponding JSON metadata file
            json_file = binn_file.replace(".binn", ".json")
            local_json_path = os.path.join(LOCAL_SAVE_DIR, json_file)
            network_json_path = os.path.join(self.network_device_raw_path, json_file)

            transferred_binn = False
            transferred_json = False

            try:
                logger.info(f"[→] Transferring {binn_file} and its metadata...")
                
                # Transfer .binn file
                shutil.copy2(local_binn_path, network_binn_path)
                if os.path.exists(network_binn_path) and os.path.getsize(local_binn_path) == os.path.getsize(network_binn_path):
                    os.remove(local_binn_path)
                    transferred_binn = True
                    logger.info(f"[✓] Transferred .binn: {binn_file}")
                else:
                    logger.warning(f"[!] Size mismatch or file not found on network for {binn_file}. Keeping local copy.")

                # Transfer .json file if it exists
                if os.path.exists(local_json_path):
                    shutil.copy2(local_json_path, network_json_path)
                    if os.path.exists(network_json_path) and os.path.getsize(local_json_path) == os.path.getsize(network_json_path):
                        os.remove(local_json_path)
                        transferred_json = True
                        logger.info(f"[✓] Transferred .json: {json_file}")
                    else:
                        logger.warning(f"[!] Size mismatch or file not found on network for {json_file}. Keeping local copy.")
                else:
                    logger.warning(f"[!] No corresponding .json metadata file found for {binn_file}.")

                if transferred_binn and (transferred_json or not os.path.exists(local_json_path)):
                    success_count += 1
                else:
                    logger.warning(f"[!] Partial transfer for {binn_file}. Check logs.")

            except Exception as e:
                logger.error(f"[!] Failed to transfer {binn_file} or its metadata: {str(e)}")
                traceback.print_exc()
                continue

        logger.info(f"Transferred {success_count} out of {len(binn_files_to_transfer)} screenshot sets.")
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

