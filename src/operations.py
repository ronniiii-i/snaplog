# src/operations.py
import os
import uuid
import subprocess
from datetime import datetime
from mss import tools
import mss
import paramiko
import logging
import traceback

os.makedirs("logs", exist_ok=True)
paramiko.util.log_to_file('logs/paramiko.log')
from src.config import (LOCAL_SAVE_DIR, CONVERTED_DIR, 
                       REMOTE_DIR, SFTP_CONFIG, DEVICE_ID_FILE)

class SnapLogOperations:
    def __init__(self):
        self.device_id = self._get_device_id()
        os.makedirs(CONVERTED_DIR, exist_ok=True)
        self.transport = None
        self.sftp = None

    def _get_device_id(self):
        """Handle device ID creation/loading"""
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, "r") as f:
                return f.read().strip()
        device_id = str(uuid.uuid4())
        with open(DEVICE_ID_FILE, "w") as f:
            f.write(device_id)
        return device_id

    def _connect_sftp(self):
        """Establish SFTP connection"""
        try:
            print("\n[SFTP] Connecting...")
            self.transport = paramiko.Transport((SFTP_CONFIG["host"], SFTP_CONFIG["port"]))
            self.transport.connect(
                username=SFTP_CONFIG["username"],
                password=SFTP_CONFIG["password"]
            )
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            print("[SFTP] Connection established")
            return True
        except Exception as e:
            print(f"[SFTP] Connection failed: {str(e)}")
            traceback.print_exc()
            import sys; sys.stdout.flush()  # Make sure logs are visible
            return False


    def _ensure_remote_dir(self):
        """Ensure remote directory exists"""
        try:
            self.sftp.stat(REMOTE_DIR)
            print(f"[SFTP] Remote directory exists: {REMOTE_DIR}")
            return True
        except IOError:
            try:
                self.sftp.mkdir(REMOTE_DIR)
                print(f"[SFTP] Created remote directory: {REMOTE_DIR}")
                return True
            except Exception as e:
                print(f"[SFTP] Failed to create directory: {str(e)}")
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
        """Transfer converted files via SFTP"""
        if not self._connect_sftp():
            return False
            
        if not self._ensure_remote_dir():
            return False
            
        files_to_transfer = os.listdir(CONVERTED_DIR)
        if not files_to_transfer:
            print("[!] No files to transfer")
            return False
            
        success_count = 0
        for file in files_to_transfer:
            local_path = os.path.join(CONVERTED_DIR, file)
            remote_path = os.path.join(REMOTE_DIR, file)
            
            try:
                print(f"[→] Transferring {file}...")
                self.sftp.put(local_path, remote_path)

                
                # Verify transfer
                if os.path.getsize(local_path) == self.sftp.stat(remote_path).st_size:
                    os.remove(local_path)
                    success_count += 1
                    print(f"[✓] Transferred {file}")
                else:
                    print(f"[!] Size mismatch for {file}")
                    
            except Exception as e:
                print(f"[!] Failed to transfer {file}: {str(e)}")
                continue
                
        return success_count > 0

    def cleanup(self):
        """Close connections"""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()

    def run_conversion_and_transfer(self):
        """Orchestrate full workflow"""
        try:
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

        finally:
            self.cleanup()
