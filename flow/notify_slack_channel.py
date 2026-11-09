"""Sends pipeline status notifications to a Slack channel via webhook.
Webhook URL is read from the SLACK_WEBHOOK_URL environment variable.
"""
import os
import urllib.request
import json

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

def send_slack(message: str):
    """Posts a message to the configured Slack webhook."""
    try:
        payload = json.dumps({"text": message}).encode()
        req = urllib.request.Request(
            SLACK_WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
        print("[SLACK] Notification sent.")
    except Exception as e:
        print(f"[SLACK ERROR] Failed to send notification: {e}")


def on_task_failure(task, task_run, state):
    """Prefect failure hook — fires a Slack alert when any pipeline task fails."""
    send_slack(f":red_circle: *MIMIC Pipeline — Task Failed*\n`{task.name}` failed\n{state.message or ''}")