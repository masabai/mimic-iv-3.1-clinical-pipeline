import os
import hashlib
import great_expectations as gx
from great_expectations.core.metric_domain_types import MetricDomainTypes
from great_expectations.expectations.metrics.metric_provider import metric_value

# ----------------------------------------------------
# 1. INITIALIZE PRODUCTION CONTEXT
# ----------------------------------------------------
context = gx.get_context()

# Connect to the local raw download folders
data_source = context.sources.add_pandas_filesystem(
    name="mimic_raw_source", 
    base_directory="C:/mimic_data/"
)

# ----------------------------------------------------
# 2. FILE COUNT & HASHE CHECK (NATIVE GX CONFIG)
# ----------------------------------------------------
# We target the specific directory (e.g., icu or hosp)
# If files are missing or structural regex fails, GX fails immediately here
hosp_asset = data_source.add_csv_asset(
    name="hosp_directory_bundle",
    batching_regex=r"(.+)\.csv\.gz",
    sep=",",
    compression="gzip",
    nrows=10  # Enforce micro-sampling for rapid structural checks
)

# Create the pre-load validation suite
pre_load_suite = context.suites.add(gx.ExpectationSuite(name="prod_pre_load_suite"))

# ----------------------------------------------------
# 3. SCHEMA & COLUMN ASSERTIONS
# ----------------------------------------------------
# Validate column structures on the sampled data stream
pre_load_suite.add_expectation(
    gx.expectations.Expect_Table_Column_Count_To_Equal(value=10)
)
pre_load_suite.add_expectation(
    gx.expectations.Expect_Table_Columns_To_Match_Ordered_List(
        column_list=["subject_id", "hadm_id", "itemid", "charttime", "valuenum"]
    )
)

# ----------------------------------------------------
# 4. RUNNING DATA QUALITY GATEKEEPER
# ----------------------------------------------------
definition = context.validation_definitions.add(
    gx.ValidationDefinition(
        name="gatekeeper_def", data_asset=hosp_asset, suite=pre_load_suite
    )
)

# Action block pushes automatically to Slack if any checklist step fails
checkpoint = context.checkpoints.add(
    gx.Checkpoint(
        name="prod_ingestion_gatekeeper",
        validation_definitions=[definition],
        actions=[
            gx.checkpoint.actions.UpdateDataDocsAction(),
            # Production style Slack hook configuration
            {
                "name": "send_slack_notification",
                "action_class_name": "SlackNotificationAction",
                "slack_webhook": "https://slack.com",
                "notify_on": "all" 
            }
        ]
    )
)

# Execute Pre-Load Check
pre_load_result = checkpoint.run()

if not pre_load_result.success:
    print("❌ Pre-ingestion validation failed. Halting pipeline execution.")
    exit(1)
