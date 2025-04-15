# transfer.py

import os
import schedule
import time
import paramiko
from config import LOCAL_SAVE_DIR, REMOTE_DIR, SFTP_CONFIG, DAILY_UPLOAD_TIME

def upload_files():
    try:
        print([*] Starting file transfer...)

        transport = paramiko.Transport((SFTP_CONFIG[hostname], SFTP_CONFIG[port]))
        transport.connect(username=SFTP_CONFIG[username], password=SFTP_CONFIG[password])
        sftp = paramiko.SFTPClient.from_transport(transport)

        for file in os.listdir(LOCAL_SAVE_DIR):
            if file.endswith(".binn"):
                local_path = os.path.join(LOCAL_SAVE_DIR, file)
                remote_filename = file.replace(".binn", ".jpg")
                remote_path = os.path.join(REMOTE_DIR, remote_filename)

                sftp.put(local_path, remote_path)
                print(f"[+] Uploaded: {file} as {remote_filename}")

                os.remove(local_path)
                print(f"[x] Deleted local copy: {file}")

        sftp.close()
        transport.close()
        print("[*] Transfer complete.")

    except Exception as e:
        print(f"[!] Error during transfer: {e}")

def schedule_transfer():
    schedule.every().day.at(DAILY_UPLOAD_TIME).do(upload_files)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_transfer()

