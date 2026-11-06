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

3. **Request and Build:** Click the download button, name your bundle (e.g., `mimic_pipeline_vocab`), and wait for Athena to process the compression package (this typically takes 10 to 15 minutes).
4. **Stage into Linux/WSL Environment:** Once the download email arrives, retrieve the file from your local Windows machine and securely move it to your target pipeline directory:

**Automation Notice:** Unlike the MIMIC data ingestion scripts, the OHDSI Athena vocabulary download **cannot be automated** via `wget` or `aws cli` due to strict session-authentication and manual bundle-generation requirements on the Athena portal. 


```bash
# Create the local vocabulary landing pad
mkdir -p ~/mimic/athena_vocab

# Copy the zip archive from your Windows Downloads partition
cp "/mnt/c/Users/<your_windows_user>/Downloads/vocabulary_download_v5_*.zip" ~/mimic/athena_vocab/

```

## STEP 4: MIMIC data
Create an account at PhysioNet.
https://physionet.org/register/
Complete the process to get credentialled access.

After that :
https://physionet.org/content/mimiciv/3.1/

ways to download
1) **Manul download** from web browser and copy to linux cp /mnt/  to mimic/mimiciv_data
Make sure to download **SHA256SUMS.txt** as GX script will need it

2) **Download using your terminal:** Copy the pre-made `wget` command (it will already have your username baked into it).

3) **Download using AWS CLI:** Copy the `aws s3 cp` or `sync` command (it will contain the secure, hidden token link to the private PhysioNet S3 bucket).

## STEP 5: Clone the repo & run
```bash
git clone https://github.com/<your-github-username>/mimic-iv-3.1-clinical-pipeline.git
cd mimic-iv-3.1-clinical-pipeline
cp .env.example .env
nano .env
docker compose up --build
```

> Everything after this is automated by the pipeline.
