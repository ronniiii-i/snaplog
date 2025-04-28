import os
import wmi
import subprocess
from datetime import datetime
from mss import tools
import mss
import logging
import traceback
import shutil


c = wmi.WMI() 
my_system = c.Win32_ComputerSystem()[0]
os.makedirs("logs", exist_ok=True)
from src.config import (LOCAL_SAVE_DIR, CONVERTED_DIR, 
                       NETWORK_PATH, DEVICE_ID_FILE)

class SnapLogOperations:
    def __init__(self):
        self.device_id = self._get_device_id()
        os.makedirs(CONVERTED_DIR, exist_ok=True)

    def _get_device_id(self):
        """Handle device ID creation/loading"""
        return f"{os.getlogin()}@{my_system.Name}"

    def _ensure_network_dir(self):
        """Ensure network directory exists"""
        try:
            if not os.path.exists(NETWORK_PATH):
                os.makedirs(NETWORK_PATH, exist_ok=True)
                print(f"[NETWORK] Created network directory: {NETWORK_PATH}")
            else:
                print(f"[NETWORK] Network directory exists: {NETWORK_PATH}")
            return True
        except Exception as e:
            print(f"[NETWORK] Failed to access or create directory: {str(e)}")
            traceback.print_exc()
            return False

    def convert_binn_to_png(self):
        """Convert .binn screenshots to .png"""
        converted_files = []
        for file in os.listdir(LOCAL_SAVE_DIR):
            if not file.endswith(".binn"):
                continue
                
            binn_path = os.path.join(LOCAL_SAVE_DIR, file)
            timestamp = file.replace("screen_", "").replace(".binn", "")
            png_name = f"{self.device_id}_{timestamp}.png"
            png_path = os.path.join(CONVERTED_DIR, png_name)

            try:
                with mss.mss() as sct:
                    raw = open(binn_path, "rb").read()
                    monitor = sct.monitors[1]
                    img = tools.to_png(raw, (monitor["width"], monitor["height"]))
                    with open(png_path, "wb") as out:
                        out.write(img)
                
                os.remove(binn_path)
                converted_files.append(png_name)
                print(f"[✓] Converted: {file} → {png_name}")
                
            except Exception as e:
                print(f"[!] Failed to convert {file}: {str(e)}")
                continue
                
        return bool(converted_files)  # Return True if any files were converted

    def transfer_files(self):
        """Transfer converted files to network path"""
        if not self._ensure_network_dir():
            return False
            
        files_to_transfer = os.listdir(CONVERTED_DIR)
        if not files_to_transfer:
            print("[!] No files to transfer")
            return False
            
        success_count = 0
        for file in files_to_transfer:
            local_path = os.path.join(CONVERTED_DIR, file)
            network_path = os.path.join(NETWORK_PATH, file)
            
            try:
                print(f"[→] Transferring {file}...")
                shutil.copy2(local_path, network_path)

                # Verify transfer
                if os.path.getsize(local_path) == os.path.getsize(network_path):
                    os.remove(local_path)
                    success_count += 1
                    print(f"[✓] Transferred {file}")
                else:
                    print(f"[!] Size mismatch for {file}")
                    
            except Exception as e:
                print(f"[!] Failed to transfer {file}: {str(e)}")
                traceback.print_exc()
                continue
                
        return success_count > 0

    def run_conversion_and_transfer(self):
        """Orchestrate full workflow"""
        try:
            if not self.convert_binn_to_png():
                print("[!] No files converted")
                return False

            transfer_result = self.transfer_files()
            if not transfer_result:
                print("[!] Transfer failed")
                return False

            return True

        except Exception as e:
            print(f"[!!!] Fatal error in transfer pipeline: {str(e)}")
            traceback.print_exc()
            return False