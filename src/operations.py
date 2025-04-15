# src/operations.py
import os
import uuid
import subprocess
from datetime import datetime
from mss import tools
import mss
import paramiko
import logging
paramiko.util.log_to_file('paramiko.log')
from src.config import (LOCAL_SAVE_DIR, CONVERTED_DIR, REMOTE_DIR, SFTP_CONFIG, DEVICE_ID_FILE)

class SnapLogOperations:
    def __init__(self):
        self.device_id = self._get_device_id()
        os.makedirs(CONVERTED_DIR, exist_ok=True)

    def _get_device_id(self):
        """Handle device ID creation/loading"""
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, "r") as f:
                return f.read().strip()
        else:
            device_id = str(uuid.uuid4())
            with open(DEVICE_ID_FILE, "w") as f:
                f.write(device_id)
            return device_id

    def convert_binn_to_png(self):
        """Replaces convert.py functionality"""
        for file in os.listdir(LOCAL_SAVE_DIR):
            if file.endswith(".binn"):
                binn_path = os.path.join(LOCAL_SAVE_DIR, file)
                timestamp = file.replace("screen_", "").replace(".binn", "")
                png_name = f"{self.device_id}_{timestamp}.png"
                png_path = os.path.join(CONVERTED_DIR, png_name)

                with mss.mss() as sct:
                    raw = open(binn_path, "rb").read()
                    monitor = sct.monitors[1]
                    img = tools.to_png(raw, (monitor["width"], monitor["height"]))
                    with open(png_path, "wb") as out:
                        out.write(img)

                print(f"[✓] Converted: {file} → {png_name}")
                os.remove(binn_path)
        return len(os.listdir(CONVERTED_DIR)) > 0  # Return True if files to transfer

    def test_sftp_connection():
        try:
            print("\n=== Testing SFTP Connection ===")
            print(f"Host: {SFTP_CONFIG['host']}:{SFTP_CONFIG['port']}")
            print(f"Username: {SFTP_CONFIG['username']}")

            transport = paramiko.Transport((SFTP_CONFIG["host"], SFTP_CONFIG["port"]))
            transport.connect(username=SFTP_CONFIG["username"], 
                            password=SFTP_CONFIG["password"])
            sftp = transport.open_sftp_client()

            # Test listing remote directory
            try:
                files = sftp.listdir(REMOTE_DIR)
                print(f"✓ Successfully accessed remote directory: {REMOTE_DIR}")
                print(f"Found {len(files)} files in remote directory")
            except IOError:
                print(f"! Remote directory doesn't exist: {REMOTE_DIR}")
                # Try creating it
                try:
                    sftp.mkdir(REMOTE_DIR)
                    print(f"✓ Created remote directory: {REMOTE_DIR}")
                except Exception as e:
                    print(f"! Failed to create directory: {str(e)}")

            sftp.close()
            transport.close()
            return True
        except Exception as e:
            print(f"! SFTP Connection failed: {str(e)}")
            return False

    def transfer_files(self):
        transport = None
        try:
            print("\n=== Transfer Debug ===")
            print(f"Local files to transfer: {os.listdir(CONVERTED_DIR)}")
            print(f"Remote destination: {REMOTE_DIR}")

            if not os.listdir(CONVERTED_DIR):
                print("! No files found in CONVERTED_DIR")
                return False

            transport = paramiko.Transport((SFTP_CONFIG["host"], SFTP_CONFIG["port"]))
            transport.connect(username=SFTP_CONFIG["username"], 
                            password=SFTP_CONFIG["password"])
            sftp = paramiko.SFTPClient.from_transport(transport)
            print("✓ SFTP connection established")

            # Verify remote directory exists
            try:
                sftp.stat(REMOTE_DIR)
            except IOError:
                print(f"! Remote directory doesn't exist, creating: {REMOTE_DIR}")
                sftp.mkdir(REMOTE_DIR)

            for file in os.listdir(CONVERTED_DIR):
                local_path = os.path.join(CONVERTED_DIR, file)
                remote_path = os.path.join(REMOTE_DIR, file)

                print(f"\nTransferring {file}...")
                print(f"Local size: {os.path.getsize(local_path)} bytes")

                sftp.put(local_path, remote_path)

                # Verify transfer
                remote_size = sftp.stat(remote_path).st_size
                print(f"Remote size: {remote_size} bytes")

                if os.path.getsize(local_path) == remote_size:
                    print("✓ Transfer verified")
                    os.remove(local_path)
                else:
                    print("! Size mismatch, keeping local copy")

            return True         
        except Exception as e:
            print(f"! Transfer failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if transport:
                transport.close()
                        
    def run_conversion_and_transfer(self):
        """Combined operation"""
        if self.convert_binn_to_png():  # Only transfer if files were converted
            return self.transfer_files()
        return False