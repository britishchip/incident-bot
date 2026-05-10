# Incident Bot

An automated incident response bot that receives alerts from Grafana, logs them as structured incidents, and posts notifications to Slack.

## Architecture
Grafana Alert → Incident Bot (/webhook) → Slack #incidents
↓
Incident Log (/incidents)

￼

## Stack

- **Python + Flask** — webhook receiver and incident logger
- **Slack Incoming Webhooks** — notification delivery
- **Kubernetes** (k3s) — container orchestration
- **Docker** — containerization

## Features

- Receives Grafana webhook payloads
- Auto-generates incident IDs (INC-0001, INC-0002...)
- Assigns severity levels (P1, P2, P3) based on alert name
- Posts colour-coded alerts to Slack
- Exposes `/incidents` endpoint for incident log
- Environment-based secrets management via `.env`

## Severity Mapping

| Level | Trigger |
|-------|---------|
| P1 | Alert name contains "critical" |
| P2 | Alert name contains "error" or "slo" |
| P3 | Everything else |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Receives Grafana alerts |
| `/incidents` | GET | Lists all logged incidents |
| `/health` | GET | Health check |

## Setup

```bash
cp .env.example .env
# Add your SLACK_WEBHOOK_URL to .env

pip install -r requirements.txt
python bot.py
```

## Deploy to Kubernetes

```bash
kubectl apply -f deployment.yaml
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL |

## Integration

Designed to work with [sre-observability](https://github.com/britishchip/sre-observability) — point Grafana contact points to `http://<bot-ip>:6000/webhook`.

## Key SRE Concepts Demonstrated

- **Automated incident response** — no manual intervention needed when alerts fire
- **Incident classification** — structured severity levels
- **Audit trail** — every incident logged with timestamp and ID
- **Secrets management** — credentials kept out of source control
