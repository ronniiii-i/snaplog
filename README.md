# Snaplog

Snaplog is a lightweight Python app that automatically captures screenshots of a computer at set intervals and stores them locally as binary files. At a scheduled time, those screenshots are moved to a remote server for review and then deleted from the local machine.

## 🔧 Features

- Starts monitoring once the system is active
- Takes screenshots every 5 minutes (configurable)
- Saves screenshots as `.binn` files in a local directory
- Moves and renames screenshots to `.png` on a remote server daily
- Automatically clears local files after successful upload

## ⚙️ Configuration

Edit `config.py` to set:

```python
SCREENSHOT_INTERVAL = 300  # seconds
DAILY_UPLOAD_TIME = "17:00"  # 24-hour format
LOCAL_SAVE_DIR = "C:/Users/YourName/Desktop/screenshots" # path to save screenshots locally
REMOTE_DIR = "/remote/server/path/screenshots/" # path to upload screenshots to
SERVER_CONFIG = {
    "hostname": "your.server.ip",
    "username": "your-username",
    "password": "your-password"
}
```

## ▶️ Usage

1. Clone the repo
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the monitor:

   ```bash
   python monitor.py
   ```

## 📦 Dependencies

- `mss` – for capturing screenshots
- `pillow` – for image processing
- `paramiko` – for SSH file transfer

Install with:

```bash
pip install mss paramiko pillow
```

## 🚧 Roadmap

- [ ] Auto-start on system boot
- [x] More secure file transfer (SFTP/SSH key support)
- [ ] Encrypted storage
- [ ] Dashboard for viewing uploads (future)

## 📄 License

MIT License. Do whatever—just don't be shady.
