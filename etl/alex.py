import base64
import subprocess
import os

PHYSIONET_USER = "maye2026"   
PHYSIONET_PASS = "21Mar1968"       

LOCAL_DOWNLOAD_DIR = "/home/moesa/mimiciv_full/data"
auth = base64.b64encode(
    f"{PHYSIONET_USER}:{PHYSIONET_PASS}".encode()
).decode()

cmd = [
    "axel", "-n", "16", "-a", "-c",
    f"--header=Authorization: Basic {auth}",
    "https://physionet.org/files/mimiciv/3.1/icu/chartevents.csv.gz"
]

subprocess.run(cmd, cwd=LOCAL_DOWNLOAD_DIR, check=False)