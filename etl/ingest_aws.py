import os
import subprocess

BASE_S3_PATH = "s3://arn:aws:s3:us-east-1:724665945834:accesspoint/mimiciv-v3-1-02/mimiciv/3.1/"
LOCAL_DOWNLOAD_DIR = "/home/moesa/mimiciv_aws/"

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
            print(f"\n✅ SUCCESS: {label} downloaded!")
        else:
            print(f"\n❌ FAILED: {label} — return code {process.returncode}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

# ── Run Downloads ──────────────────────────────────────────
run_aws_s3_sync("hosp/", "hosp/", "MIMIC-IV hosp module")
run_aws_s3_sync("icu/",  "icu/",  "MIMIC-IV icu module")

print("\n All downloads complete!")
