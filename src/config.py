# src/config.py
import os
import sys
import wmi
import json
from dotenv import load_dotenv

# Load environment variables (if any)
load_dotenv()

# Initialize WMI for system information
c = wmi.WMI()
my_system = c.Win32_ComputerSystem()[0]

# ====================================================================
# Client-specific paths and settings
# ====================================================================

# Base directory for local screenshots (e.g., user's home directory)
# LOCAL_SAVE_DIR = os.path.expanduser("~")


if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    # Use AppData\Roaming for persistent user-specific data
    local_base_path = os.path.join(os.getenv('APPDATA'), 'SnapLogClient')
else:
    # Running as a regular Python script
    local_base_path = os.path.dirname(os.path.abspath(__file__))

LOCAL_SAVE_DIR = os.path.join(local_base_path, 'temp_raw_data')
# You'll also need to ensure the logs folder is handled similarly
LOGS_DIR = os.path.join(local_base_path, 'logs')

# Directory for converted files (on the client, though conversion is now server-side,
# this might be used for temporary storage or if client-side conversion is re-introduced)
CONVERTED_DIR = os.path.join(LOCAL_SAVE_DIR, "converted")

# Device ID for this client, used to identify it on the server
# This should be unique for each client machine
DEVICE_ID = f"{os.getlogin()}@{my_system.Name}"

# ====================================================================
# Network paths and centralized configuration
# ====================================================================

# This is the base path on your shared network drive where all client data will reside.
# IMPORTANT: You MUST ensure this path is accessible by both clients and the server.
# For example, if Z: is a mapped network drive, ensure it's correctly mapped on all machines.
# NETWORK_BASE_PATH = "C:/snaplog_data/" # Example: Adjust this to your actual shared network pathpath
# NETWORK_BASE_PATH = f"X:/{os.getlogin()}@{my_system.Name}/" # Example: Adjust this to your actual shared network pathpath
NETWORK_BASE_PATH = "X:/" # Example: Adjust this to your actual shared network pathpath

# Path to the central configuration file for all clients
CLIENT_CONFIG_FILE = os.path.join(NETWORK_BASE_PATH, "client_configs.json")

# Default values for client settings if not found in the central config
DEFAULT_SCREENSHOT_INTERVAL = 30  # 5 minutes
DEFAULT_UPLOAD_TYPE = "periodic"      # "daily" or "periodic"
DEFAULT_UPLOAD_VALUE = "150"     # HH:MM for daily, seconds for periodic (e.g., 3600 for 1 hour)

def load_client_config():
    """
    Loads the configuration for the current device from the central JSON file.
    If the file or the device's entry doesn't exist, it returns default values.
    """
    config = {
        "screenshot_interval": DEFAULT_SCREENSHOT_INTERVAL,
        "upload_type": DEFAULT_UPLOAD_TYPE,
        "upload_value": DEFAULT_UPLOAD_VALUE,
    }
    try:
        # Ensure the base network path exists before trying to read config
        os.makedirs(NETWORK_BASE_PATH, exist_ok=True)
        
        if os.path.exists(CLIENT_CONFIG_FILE):
            with open(CLIENT_CONFIG_FILE, 'r') as f:
                all_configs = json.load(f)
            if DEVICE_ID in all_configs:
                loaded_config = all_configs[DEVICE_ID]
                # Update config with loaded values, using defaults if a key is missing
                config["screenshot_interval"] = loaded_config.get("screenshot_interval", DEFAULT_SCREENSHOT_INTERVAL)
                config["upload_type"] = loaded_config.get("upload_type", DEFAULT_UPLOAD_TYPE)
                config["upload_value"] = loaded_config.get("upload_value", DEFAULT_UPLOAD_VALUE)
                print(f"[CONFIG] Loaded configuration for {DEVICE_ID}: {config}")
            else:
                print(f"[CONFIG] No specific configuration found for {DEVICE_ID}. Using defaults.")
        else:
            print(f"[CONFIG] Central configuration file not found at {CLIENT_CONFIG_FILE}. Using defaults.")
    except json.JSONDecodeError:
        print(f"[CONFIG] Error decoding JSON from {CLIENT_CONFIG_FILE}. Using defaults.")
    except Exception as e:
        print(f"[CONFIG] An error occurred loading config: {e}. Using defaults.")
    
    return config