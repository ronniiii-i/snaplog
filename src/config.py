import os
from dotenv import load_dotenv
load_dotenv()


SCREENSHOT_INTERVAL = 10  # 5 minutes

LOCAL_SAVE_DIR = os.path.expanduser("~/Desktop/screenshots")

CONVERTED_DIR = os.path.join(LOCAL_SAVE_DIR, "converted")

DEVICE_ID_FILE = os.path.join(LOCAL_SAVE_DIR, "device_id.txt") 

# os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
# os.makedirs(CONVERTED_DIR, exist_ok=True)

REMOTE_DIR = "/home/username/screenshots/"

DAILY_UPLOAD_TIME = "17:00"  # 5 PM

SFTP_CONFIG = {
    "host": os.getenv("SFTP_HOST"),
    "port": 22,
    "username": os.getenv("SFTP_USER"),
    "password": os.getenv("SFTP_PASS")
}

