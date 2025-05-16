# import os
# import schedule
# import time
# import shutil
# from config import CONVERTED_DIR, NETWORK_PATH, DAILY_UPLOAD_TIME

# def transfer_files():
#     try:
#         print("[*] Starting file transfer...")

#         # Create network path directory if it doesn't exist
#         os.makedirs(NETWORK_PATH, exist_ok=True)

#         for file in os.listdir(CONVERTED_DIR):
#             local_path = os.path.join(CONVERTED_DIR, file)
#             network_path = os.path.join(NETWORK_PATH, file)
            
#             # Copy file to network path
#             shutil.copy2(local_path, network_path)
#             print(f"[+] Transferred: {file}")
            
#             # Remove local file after transfer
#             os.remove(local_path)
#             print(f"[x] Deleted local copy: {file}")

#         print("[*] Transfer complete.")

#     except Exception as e:
#         print(f"[!] Error during transfer: {e}")

# def schedule_transfer():
#     schedule.every().day.at(DAILY_UPLOAD_TIME).do(transfer_files)

#     while True:
#         schedule.run_pending()
#         time.sleep(60)

# if __name__ == "__main__":
#     # schedule_transfer()
#     transfer_files()