# Inside your step7_run_dbt.py automation script
import subprocess

# 1. Parse and build your schema translation references
subprocess.run(["dbt", "seed", "--project-dir", "dbt_project", "--profiles-dir", "dbt_project"], check=True)

# 2. Run the clinical data while completely blocking the X-Ray models
print("[DBT] Running MIMIC-IV Clinical models (Excluding X-Rays)...")
subprocess.run([
    "dbt", "run", 
    "--project-dir", "dbt_project", 
    "--profiles-dir", "dbt_project", 
    "--exclude", "tag:mimic_cxr"          # <-- ADD THIS EXCLUSION FLAG
], check=True)
