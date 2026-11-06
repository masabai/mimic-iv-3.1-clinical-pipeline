import os
import subprocess

BASE_S3_PATH = os.environ["BASE_S3_PATH"]
LOCAL_DOWNLOAD_DIR = os.environ.get("LOCAL_DOWNLOAD_DIR", "/data")

def run_aws_s3_sync(s3_subpath, local_subpath, label):
    s3_path    = BASE_S3_PATH + s3_subpath
    local_path = LOCAL_DOWNLOAD_DIR + local_subpath

    print(f"\n{'='*60}")
    print(f"DOWNLOADING: {label}")
    print(f"FROM: {s3_path}")
    print(f"TO:   {local_path}")
    print(f"{'='*60}\n")

    aws_command = [
        "aws", "s3", "sync",
        s3_path,
        local_path,
        "--request-payer", "requester",
        "--region", "us-east-1"
    ]

    env = os.environ.copy()

    try:
        process = subprocess.Popen(
            aws_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()

        if process.returncode == 0:
            print(f"\n [STEP 2: INGEST DATA FROM AWS] PASS SUCCESS: {label} downloaded!")
        else:
            print(f"\nFAILED: {label} — return code {process.returncode}")

    except Exception as e:
        print(f"\nERROR: {e}")

# ── Run Downloads ──────────────────────────────────────────
run_aws_s3_sync("hosp/", "hosp/", "MIMIC-IV hosp module")
run_aws_s3_sync("icu/",  "icu/",  "MIMIC-IV icu module")

# Download root-level manifest files (SHA256SUMS.txt etc.)
print("\nDownloading root-level manifest files...")
subprocess.run([
    "aws", "s3", "sync",
    BASE_S3_PATH, LOCAL_DOWNLOAD_DIR,
    "--request-payer", "requester",
    "--region", "us-east-1",
    "--exclude", "*",
    "--include", "SHA256SUMS.txt",
], env=os.environ.copy())

print("\n All downloads complete!")
