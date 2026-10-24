import urllib.request
import json

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack(message: str):
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
    send_slack(f":red_circle: *MIMIC Pipeline — Task Failed*\n`{task.name}` failed\n{state.message or ''}")