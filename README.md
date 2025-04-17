# SnapLog - Automated Screenshot Monitor

## Overview

SnapLog is an automated screenshot monitoring system that:

- Takes periodic screenshots of your primary monitor
- Stores them locally in a binary format (.binn)
- Converts them to PNG format with device-specific identifiers
- Transfers them to a remote server via SFTP at a scheduled time

## Features

- **Scheduled Capture**: Takes screenshots at regular intervals (default: 5 minutes)
- **Secure Transfer**: Uses SFTP for encrypted file transfers
- **Device Identification**: Generates unique device IDs for screenshot tracking
- **Automatic Conversion**: Converts binary screenshots to standard PNG format
- **Scheduled Uploads**: Transfers files daily at a specified time (default: 5 PM)
- **Logging**: Comprehensive logging for monitoring and debugging

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/snaplog.git
   cd snaplog
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your SFTP credentials:

   ```env
   SFTP_HOST=your.sftp.server
   SFTP_USER=your_username
   SFTP_PASS=your_password
   ```

## Usage

Run the main application:

```bash
python main.py
```

The application will:

1. Create necessary directories (`~/Desktop/screenshots` and subdirectories)
2. Start capturing screenshots every 5 minutes (configurable)
3. Run conversion and transfer at the scheduled time (default: 5 PM)
4. Exit after successful transfer (should be run as a daily scheduled task)

## Configuration

Modify `src/config.py` to adjust settings:

```python
SCREENSHOT_INTERVAL = 300  # Capture interval in seconds (5 minutes)
DAILY_UPLOAD_TIME = "17:00"  # 24-hour format
LOCAL_SAVE_DIR = "~/Desktop/screenshots"  # Local storage location
REMOTE_DIR = "/home/username/screenshots/"  # Remote directory path
```

## File Structure

```tree
snaplog/
├── src/
│   ├── config.py       # Configuration settings
│   ├── monitor.py      # Screenshot monitoring service
│   └── operations.py   # File conversion and transfer operations
├── main.py             # Main application entry point
├── .env                # Environment variables (not tracked by git)
└── logs/               # Log files directory
```

## Requirements

- Python 3.7+
- Required packages (see `requirements.txt`):
  - `mss` (for screenshot capture)
  - `paramiko` (for SFTP transfers)
  - `python-dotenv` (for environment variables)

## Logging

Application logs are stored in `logs/snaplog.log`. SFTP-specific logs are stored in `logs/paramiko.log`.

## Notes

- The application will create a unique device ID on first run (stored in `device_id.txt`)
- After successful transfer, the application exits and should be restarted (ideal for daily scheduled tasks)
- Keyboard interrupt (Ctrl+C) will gracefully shut down the monitoring service

## License

[MIT License](LICENSE) Do whatever—just don't be shady.