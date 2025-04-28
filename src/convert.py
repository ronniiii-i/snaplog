import wmi
import os
import subprocess
from datetime import datetime
from mss import tools
import mss

from config import LOCAL_SAVE_DIR, CONVERTED_DIR

c = wmi.WMI() 
my_system = c.Win32_ComputerSystem()[0]

DEVICE_ID = f"{os.getlogin()}@{my_system.Name}"
print(f"Device ID: {DEVICE_ID}")

# Create folder if it doesn't exist
os.makedirs(CONVERTED_DIR, exist_ok=True)


def convert_binn_to_png():
    for file in os.listdir(LOCAL_SAVE_DIR):
        if file.endswith(".binn"):
            binn_path = os.path.join(LOCAL_SAVE_DIR, file)
            timestamp =  file.replace("screen_", "").replace(".binn", "")
            png_name = f"{DEVICE_ID}_{timestamp}.png"
            png_path = os.path.join(CONVERTED_DIR, png_name)

            with mss.mss() as sct:
                raw = open(binn_path, "rb").read()
                monitor = sct.monitors[1]
                img = tools.to_png(raw, (monitor["width"], monitor["height"]))
                with open(png_path, "wb") as out:
                    out.write(img)

            print(f"[✓] Converted: {file} → {png_name}")
            os.remove(binn_path)


def trigger_transfer():
    try:
        subprocess.run(["python", "transfer.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[x] Transfer failed: {e}")


if __name__ == "__main__":
    convert_binn_to_png()
    trigger_transfer()
