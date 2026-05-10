from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
incidents = []


def severity(alert):
    labels = alert.get("labels", {})
    annotations = alert.get("annotations", {})
    name = labels.get("alertname", "Unknown")
    if "critical" in name.lower():
        return "P1"
    elif "error" in name.lower() or "slo" in name.lower():
        return "P2"
    return "P3"


def create_incident(alert):
    incident = {
        "id": f"INC-{len(incidents) + 1:04d}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "title": alert.get("labels", {}).get("alertname", "Unknown Alert"),
        "severity": severity(alert),
        "status": alert.get("status", "firing"),
        "labels": alert.get("labels", {}),
        "annotations": alert.get("annotations", {}),
        "generator_url": alert.get("generatorURL", ""),
    }
    incidents.append(incident)
    return incident


def post_to_slack(incident):
    color = {"P1": "#FF0000", "P2": "#FF9900", "P3": "#36a64f"}.get(
        incident["severity"], "#cccccc"
    )
    status_emoji = "🔥" if incident["status"] == "firing" else "✅"

    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"{status_emoji} [{incident['severity']}] {incident['title']}",
                "fields": [
                    {"title": "Incident ID", "value": incident["id"], "short": True},
                    {
                        "title": "Status",
                        "value": incident["status"].upper(),
                        "short": True,
                    },
                    {"title": "Time", "value": incident["timestamp"], "short": False},
                ],
                "footer": "SRE Incident Bot",
            }
        ]
    }

    requests.post(SLACK_WEBHOOK_URL, json=payload)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    alerts = data.get("alerts", [])
    for alert in alerts:
        incident = create_incident(alert)
        post_to_slack(incident)
    return jsonify({"status": "ok", "incidents_created": len(alerts)})


@app.route("/incidents", methods=["GET"])
def list_incidents():
    return jsonify(incidents)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
