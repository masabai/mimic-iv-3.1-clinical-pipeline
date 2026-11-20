
# AWS CLI + PhysioNet Handshake Setup
To use `step2_ingest_aws.py`, you need an AWS account linked to your PhysioNet account. You can also check your exact AWS charges right away using the CLI command in the [Monitor Billing](#monitor-billing) section below.

> [!CAUTION]
> **Don't skip this for `wget` or manual browser downloads!**
> * **Speed & Cost:** PhysioNet's direct download servers are extremely slow (`wget` can take **7+ days** and still not finish). Setting up AWS takes **~10 minutes** once, and then the entire dataset downloads in **~2 minutes for ~$0.01**.
> * **Easy Setup with AI:** Don't let the length of this guide intimidate you. As soon as you log into the **AWS Console**, click the **Amazon Q** icon on the right sidebar—it will walk you through creating your IAM user and keys step by step.


---

## Step 1: Get MIMIC-IV Access on PhysioNet

1. Create an account at https://physionet.org and complete credentialing
2. Request access to MIMIC-IV at https://physionet.org/content/mimiciv/3.1/
3. Once approved, go to https://physionet.org/settings/cloud/
4. Note your **Account**, **User ID**, and **ARN** — you will need these to verify the handshake later

---

## Step 2: Install AWS CLI

```bash
sudo apt update && sudo apt install awscli -y
```

---

## Step 3: Create an IAM User & Access Keys

1. Log into the AWS Console
2. Search for **IAM** → click **Users** → create a user or select an existing one
3. Go to **Security credentials** tab → scroll to **Access keys** → click **Create access key**
4. Choose **Command Line Interface (CLI)**, confirm, and click **Create**
5. Copy both keys immediately — AWS will never show the Secret Key again

---

## Step 4: Configure AWS CLI

```bash
aws configure
```

Enter when prompted:
- `AWS Access Key ID` — your key from Step 3
- `AWS Secret Access Key` — your secret from Step 3
- `Default region name` — `us-east-1` (MIMIC-IV is stored in us-east-1)
- `Default output format` — `json`

Credentials are saved to `~/.aws/credentials`.

---

## Step 5: Link AWS Account to PhysioNet

1. Go to https://physionet.org/content/mimiciv/3.1/
2. Scroll down and click **Enable AWS Web Service Access**
3. Enter your AWS **Account ID** (12-digit number, found top-right in AWS Console)
4. PhysioNet will authorize your account to access the S3 access point

---

## Step 6: Verify the Handshake

```bash
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "<your-iam-user-id>",
    "Account": "<your-aws-account-id>",
    "Arn": "arn:aws:iam::<your-aws-account-id>:user/<your-iam-username>"
}
```

Make sure **Account** and **ARN** match what PhysioNet shows at https://physionet.org/settings/cloud/

Then confirm S3 access:
```bash
aws s3 ls <BASE_S3_PATH> --request-payer requester --region us-east-1
```

`BASE_S3_PATH` is the S3 access point URL shown on the PhysioNet MIMIC-IV page after enabling AWS access. Set it in your `.env` file.

---

## Step 7: Set Environment Variables

```bash
cp .env.example .env
```

Fill in your values:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
BASE_S3_PATH=s3://arn:aws:s3:<region>:<account-id>:accesspoint/<accesspoint-name>/mimiciv/3.1/
```

---


## Monitor Billing

```bash
aws ce get-cost-and-usage \
  --time-period Start=YYYY-MM-01,End=YYYY-MM-DD \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --region us-east-1
```
