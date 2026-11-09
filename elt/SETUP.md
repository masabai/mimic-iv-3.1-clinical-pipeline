# Requirements
16GB RAM + 200GB Hard Disk

## STEP 1: Install Ubuntu 
Download and install Ubuntu from https://ubuntu.com/download/desktop
Follow the on-screen installer — default options are fine.

> **Important:** Note down your username and password during installation — you will need it for sudo commands later.


## STEP 2: Install Git, Docker & Docker Compose
Open terminal and run:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose unzip
```

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify:
```bash
docker --version
docker compose version
```

## STEP 3: Athena Vocabulary (Manual — one time)
1. Create account at https://athena.ohdsi.org
2. select the exact **22 vocabularies** required by the CogStack baseline pipeline:
   * *Clinical Standards:* SNOMED, LOINC, RxNorm, CPT4, HCPCS, ATC
   * *Classifications:* ICD9CM, ICD9Proc, ICD10CM
   * *Source & Metadata:* NDC, SPL, Gender, Race, Ethnicity, Currency
   * *Administrative:* CMS Place of Service, Revenue Code, NUCC, Medicare Specialty, ABMS
   * *OHDSI Extensions:* OMOP Extension, RxNorm Extension

request download OR Go to
https://github.com/CogStack/dbt_mimic_omop/blob/main/README.md
Clicking on **here** link will preselect all required vocabulary

3. **Request and Build:** Click the download button, name your bundle (e.g., `mimic_pipeline_vocab`), and wait for Athena to process the compression package and wait for the email to access (this typically takes 10 to 15 minutes).
4. **Stage into Linux/WSL Environment:** Once the download email arrives, download the bundle and retrieve the file from your local Windows machine and securely move it to your target pipeline directory:


```bash
# Create the local vocabulary landing pad
mkdir -p ~/mimic/athena_vocab

# Copy the zip archive from your Windows Downloads partition
cp "/mnt/c/Users/<your_windows_user>/Downloads/vocabulary_download_v5_*.zip" ~/mimic/athena_vocab/

```

**Automation Notice:** Unlike the MIMIC data ingestion scripts, the OHDSI Athena vocabulary download **cannot be automated** via `wget` or `aws cli` due to strict session-authentication and manual bundle-generation requirements on the Athena portal. 


## STEP 4: MIMIC data
Create an account at PhysioNet.
https://physionet.org/register/
Complete the process to get credentialled access.

After that :
https://physionet.org/content/mimiciv/3.1/

ways to download
1) **Manul download** from web browser and copy to linux cp /mnt/  to mimic/mimiciv_data
Make sure `SHA256SUMS.txt` is included in the download (needed for hash verification).

2) **Download using your terminal:** Copy the pre-made `wget` command from the PhysioNet page (your username is pre-filled). Paste it into a tmux session — see `etl/README.md` for the tmux workflow. wget takes 20+ hrs and will die if your session drops without tmux.

3) **Download using AWS CLI:**  Refer to AWS_PHYSIONET_SETUP.md
Copy the `aws s3 cp` or `sync` command (it will contain the secure, hidden token link to the private PhysioNet S3 bucket). 

## STEP 5: Clone the repo & run
```bash
git clone https://github.com/masabai/mimic-iv-3.1-clinical-pipeline.git
cd mimic-iv-3.1-clinical-pipeline
cp .env.example .env
nano .env        # fill in AWS credentials — see VS Code tip below if you prefer a GUI editor
docker compose up --build
```

> Everything after this is automated by the pipeline.

---

## Bonus: Edit Files with VS Code (instead of nano)

If you are developing on Windows via WSL, using Visual Studio Code is a much friendlier way to view and edit `.env` files, Python scripts, or data configurations without touching `nano`.

### 1. Install VS Code
Download and install the Windows version from [code.visualstudio.com](https://code.visualstudio.com).

### 2. Install the WSL Extension
Open VS Code, go to the Extensions view (`Ctrl+Shift+X`), search for **WSL**, and click **Install**.

### 3. Open Your Project in WSL

* **Option A (From your WSL terminal - Fastest):**
  Navigate to your pipeline directory and open it directly:
  ```bash
  cd mimic-iv-3.1-clinical-pipeline
  code .
  ```
  *(Note: The first time you run this, WSL will quickly set up the VS Code server components automatically.)*

* **Option B (From VS Code UI):**
  1. Click the remote indicator button (the `><` icon) in the very bottom-left corner of VS Code.
  2. Select **Connect to WSL**.
  3. Go to **File → Open Folder** and navigate to your Linux project directory.

* **Tip:** If you are using VS Code, you can select **Terminal → New Terminal** from the top menu to run your `docker compose` or `git` commands right inside the editor. This keeps your code view and your terminal window in a single screen.
