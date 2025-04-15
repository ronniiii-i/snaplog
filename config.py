# config.py
import os

# Time in seconds between screenshots
SCREENSHOT_INTERVAL = 300  # 5 minutes

# Local save directory
LOCAL_SAVE_DIR = os.path.expanduser("~/Desktop/screenshots")

# Remote server directory (this is just a string path, not code)
REMOTE_DIR = "/home/username/screenshots/"

# Optional: if you need upload time logic elsewhere
DAILY_UPLOAD_HOUR = 17  # 5 PM
DAILY_UPLOAD_MINUTE = 0

# SFTP_CONFIG = {
#     hostname: your.server.ip,
#     port: 22,
#     username: your_user,
#     password: your_password,  # consider using SSH key for prod
# }

